"""
响应效率评估器
"""

from typing import Any, Dict

from agenteval.evaluators.base import BaseEvaluator
from agenteval.models.task import TestCase
from agenteval.models.result import MetricScore


class EfficiencyEvaluator(BaseEvaluator):
    """响应效率评估器

    评估Agent的响应效率，包括延迟、Token消耗和成本。

    Attributes:
        latency_threshold_ms: 延迟阈值毫秒 (默认: 5000)
        token_threshold: Token消耗阈值 (默认: 1000)

    评分标准：
        延迟:
            - < 2s: 1.0 (优秀)
            - 2-5s: 0.8 (良好)
            - 5-10s: 0.6 (一般)
            - > 10s: 0.4 (较差)

    Example:
        >>> evaluator = EfficiencyEvaluator(latency_threshold_ms=3000)
        >>> score = await evaluator.evaluate(test_case, agent_response, context)
        >>> print(f"Efficiency: {score.score:.2f}")
    """

    def __init__(self, config: Dict[str, Any] | None = None, **kwargs):
        """初始化EfficiencyEvaluator

        Args:
            config: 配置字典
            **kwargs: 其他配置参数
        """
        if config is None:
            config = {}
        config.update(kwargs)

        super().__init__(config)
        self.latency_threshold_ms = self.config.get("latency_threshold_ms", 5000)
        self.token_threshold = self.config.get("token_threshold", 1000)

    async def evaluate(
        self,
        test_case: TestCase,
        agent_response: str,
        context: Dict[str, Any] | None = None,
    ) -> MetricScore:
        """执行效率评估

        Args:
            test_case: 测试用例
            agent_response: Agent响应
            context: 上下文（应包含latency_ms和token_usage）

        Returns:
            MetricScore: 评估分数
        """
        context = context or {}
        latency_ms = context.get("latency_ms", 0.0)
        token_usage = context.get("token_usage", {})

        # 计算延迟分数
        latency_score = self._calculate_latency_score(latency_ms)

        # 计算Token效率分数
        total_tokens = token_usage.get("total_tokens", 0) or token_usage.get("total", 0)
        token_score = self._calculate_token_score(total_tokens)

        # 计算响应长度效率
        response_length = len(agent_response)
        length_score = self._calculate_length_score(response_length, total_tokens)

        # 综合分数 (延迟占60%，Token占30%，长度效率占10%)
        overall_score = 0.6 * latency_score + 0.3 * token_score + 0.1 * length_score

        return MetricScore(
            name="efficiency",
            score=overall_score,
            weight=self.weight,
            details=(
                f"Latency: {latency_ms:.0f}ms, "
                f"Tokens: {total_tokens}, "
                f"Response length: {response_length}"
            ),
            metadata={
                "latency_ms": latency_ms,
                "latency_score": latency_score,
                "token_usage": token_usage,
                "total_tokens": total_tokens,
                "token_score": token_score,
                "response_length": response_length,
                "length_score": length_score,
                "latency_threshold_ms": self.latency_threshold_ms,
                "token_threshold": self.token_threshold,
            },
        )

    def _calculate_latency_score(self, latency_ms: float) -> float:
        """计算延迟分数

        Args:
            latency_ms: 延迟毫秒

        Returns:
            float: 延迟分数 (0-1)
        """
        if latency_ms < 2000:
            return 1.0
        elif latency_ms < 5000:
            return 0.8
        elif latency_ms < 10000:
            return 0.6
        elif latency_ms < 20000:
            return 0.4
        else:
            return 0.2

    def _calculate_token_score(self, total_tokens: int) -> float:
        """计算Token效率分数

        Args:
            total_tokens: 总Token消耗

        Returns:
            float: Token分数 (0-1)
        """
        if total_tokens <= 0:
            return 1.0
        elif total_tokens <= 200:
            return 1.0
        elif total_tokens <= 500:
            return 0.9
        elif total_tokens <= 1000:
            return 0.7
        elif total_tokens <= 2000:
            return 0.5
        else:
            return 0.3

    def _calculate_length_score(self, response_length: int, total_tokens: int) -> float:
        """计算响应长度效率分数

        检查响应长度是否合理（不过长也不过短）

        Args:
            response_length: 响应字符数
            total_tokens: 总Token消耗

        Returns:
            float: 长度效率分数 (0-1)
        """
        if response_length <= 0:
            return 0.0
        elif response_length < 20:
            return 0.5  # 太短
        elif response_length < 100:
            return 0.8
        elif response_length < 2000:
            return 1.0  # 合理长度
        elif response_length < 5000:
            return 0.8
        else:
            return 0.6  # 太长
