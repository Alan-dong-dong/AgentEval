"""
简单模式API - 快速评估
"""

import asyncio
from typing import Any, Callable, Dict, Union

from agenteval.core.engine import EvaluationEngine
from agenteval.models.task import TestCase, AgentConfig
from agenteval.evaluators.correctness import CorrectnessEvaluator
from agenteval.evaluators.efficiency import EfficiencyEvaluator
from agenteval.adapters.base import CallableAdapter


class QuickEval:
    """快速评估类

    为初学者提供最简化的评估接口。

    Example:
        >>> from agenteval import quick_eval
        >>> result = quick_eval(my_agent, "What is 2+2?", expected="4")
        >>> print(f"Score: {result['score']:.2f}")
    """

    def __init__(self):
        self.engine = EvaluationEngine()
        self._setup_default_evaluators()

    def _setup_default_evaluators(self):
        """设置默认评估器"""
        self.engine.add_evaluators(
            [
                CorrectnessEvaluator(),
                EfficiencyEvaluator(),
            ]
        )

    def evaluate(
        self,
        agent: Union[Callable, Any],
        prompt: str,
        expected: str | None = None,
    ) -> Dict[str, Any]:
        """最简单的评估接口

        Args:
            agent: Agent函数或实例
            prompt: 测试提示词
            expected: 期望输出（可选）

        Returns:
            Dict: 评估结果

        Example:
            >>> result = quick_eval(my_agent, "What is 2+2?", expected="4")
        """
        return asyncio.run(self._evaluate_async(agent, prompt, expected))

    async def _evaluate_async(
        self,
        agent: Union[Callable, Any],
        prompt: str,
        expected: str | None = None,
    ) -> Dict[str, Any]:
        """异步评估实现

        Args:
            agent: Agent函数或实例
            prompt: 测试提示词
            expected: 期望输出（可选）

        Returns:
            Dict: 评估结果
        """
        # 创建测试用例
        test_case = TestCase(
            name="quick_eval",
            input_message=prompt,
            expected_output=expected,
        )

        # 创建Agent配置
        agent_config = AgentConfig(
            framework="callable",
            agent_callable=agent if callable(agent) else None,
            agent_instance=agent if not callable(agent) else None,
        )

        # 创建适配器
        adapter = CallableAdapter(agent_config)
        self.engine.set_adapter(adapter)

        # 执行评估
        result = await self.engine.evaluate_single(test_case)

        return {
            "success": result.success,
            "score": result.overall_score,
            "response": result.agent_response,
            "latency_ms": result.latency_ms,
            "error": result.error_message if not result.success else None,
            "details": {
                s.name: {"score": s.score, "details": s.details} for s in result.scores
            },
        }


# 全局便捷实例
_quick_eval_instance = QuickEval()


def quick_eval(
    agent: Union[Callable, Any],
    prompt: str,
    expected: str | None = None,
) -> Dict[str, Any]:
    """快速评估Agent

    一行代码完成评估，适合快速验证和测试。

    Args:
        agent: Agent函数或实例
            - 函数: def my_agent(prompt: str) -> str
            - 类实例: 实现了__call__方法的类
        prompt: 测试提示词
        expected: 期望输出（可选）

    Returns:
        Dict: 评估结果
            - success: bool - 是否成功执行
            - score: float - 综合分数 (0-1)
            - response: str - Agent响应
            - latency_ms: float - 响应延迟
            - details: Dict - 详细评估结果

    Example:
        >>> # 评估简单函数
        >>> def my_agent(prompt):
        ...     return "The answer is 4"
        >>> result = quick_eval(my_agent, "What is 2+2?", expected="4")
        >>> print(f"Score: {result['score']:.2f}")

        >>> # 评估类实例
        >>> class MyAgent:
        ...     def __call__(self, prompt):
        ...         return "Hello!"
        >>> result = quick_eval(MyAgent(), "Say hello")
    """
    return _quick_eval_instance.evaluate(agent, prompt, expected)
