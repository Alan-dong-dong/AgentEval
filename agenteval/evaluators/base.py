"""
评估器基类
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from agenteval.models.task import TestCase
from agenteval.models.result import MetricScore


class BaseEvaluator(ABC):
    """评估器基类

    所有自定义评估器必须继承此类并实现evaluate方法。

    Attributes:
        name: 评估器名称
        config: 评估器配置
        weight: 评估器权重

    Example:
        >>> class MyEvaluator(BaseEvaluator):
        ...     async def evaluate(self, test_case, agent_response, context):
        ...         score = 0.95
        ...         return MetricScore(name="custom", score=score)
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        self.weight = self.config.get("weight", 1.0)

    @abstractmethod
    async def evaluate(
        self,
        test_case: TestCase,
        agent_response: str,
        context: Dict[str, Any] | None = None,
    ) -> MetricScore:
        """执行评估

        Args:
            test_case: 测试用例
            agent_response: Agent的响应
            context: 额外上下文信息

        Returns:
            MetricScore: 评估分数
        """
        pass

    def validate_config(self) -> bool:
        """验证配置是否有效

        Returns:
            bool: 配置是否有效
        """
        return True

    def get_info(self) -> Dict[str, Any]:
        """获取评估器信息

        Returns:
            Dict: 评估器信息
        """
        return {
            "name": self.name,
            "description": self.__doc__ or "",
            "weight": self.weight,
            "config": self.config,
        }


class LLMBasedEvaluator(BaseEvaluator):
    """基于LLM的评估器基类

    使用LLM进行评估的评估器基类，提供LLM调用的通用方法。

    Attributes:
        model: 用于评估的LLM模型
        client: LLM客户端
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config)
        self.model = self.config.get("model", "gpt-4")
        self.client = None

    def _init_client(self):
        """初始化LLM客户端"""
        if self.client is None:
            try:
                import openai

                self.client = openai.AsyncOpenAI()
            except ImportError:
                raise ImportError(
                    "openai package is required for LLMBasedEvaluator. "
                    "Install it with: pip install openai"
                )

    async def _call_llm(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
    ) -> str:
        """调用LLM进行评估

        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            temperature: 温度参数

        Returns:
            str: LLM响应
        """
        self._init_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )

        return response.choices[0].message.content or ""

    def _parse_score_from_response(self, response: str) -> float:
        """从LLM响应中解析分数

        Args:
            response: LLM响应文本

        Returns:
            float: 解析的分数 (0-1)
        """
        import re

        # 尝试匹配 "分数: XX" 或 "Score: XX" 格式
        patterns = [
            r"分数[：:]\s*(\d+(?:\.\d+)?)",
            r"[Ss]core[：:]\s*(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)\s*/\s*100",
            r"(\d+(?:\.\d+)?)%",
        ]

        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                score = float(match.group(1))
                # 归一化到 0-1
                if score > 1:
                    score = score / 100
                return min(max(score, 0.0), 1.0)

        # 默认分数
        return 0.5


class RuleBasedEvaluator(BaseEvaluator):
    """基于规则的评估器基类

    使用规则进行评估的评估器基类。

    Attributes:
        rules: 评估规则列表
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config)
        self.rules: List[Any] = []

    def add_rule(self, rule):
        """添加评估规则

        Args:
            rule: 评估规则函数
        """
        self.rules.append(rule)

    async def evaluate(
        self,
        test_case: TestCase,
        agent_response: str,
        context: Dict[str, Any] | None = None,
    ) -> MetricScore:
        """执行规则评估

        Args:
            test_case: 测试用例
            agent_response: Agent响应
            context: 上下文

        Returns:
            MetricScore: 评估分数
        """
        if not self.rules:
            return MetricScore(
                name=self.name,
                score=1.0,
                weight=self.weight,
                details="No rules defined",
            )

        scores = []
        details = []

        for rule in self.rules:
            try:
                score, detail = rule(test_case, agent_response, context or {})
                scores.append(score)
                details.append(detail)
            except Exception as e:
                scores.append(0.0)
                details.append(f"Rule error: {str(e)}")

        avg_score = sum(scores) / len(scores) if scores else 0.0

        return MetricScore(
            name=self.name,
            score=avg_score,
            weight=self.weight,
            details="; ".join(details),
            metadata={"rule_scores": scores},
        )
