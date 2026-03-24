"""
工具使用评估器
"""

from typing import Any, Dict, List

from agenteval.evaluators.base import BaseEvaluator
from agenteval.models.task import TestCase
from agenteval.models.result import MetricScore


class ToolUsageEvaluator(BaseEvaluator):
    """工具使用评估器

    评估Agent是否正确选择和使用了工具。
    计算工具调用的精确率(Precision)、召回率(Recall)和F1分数。

    Attributes:
        strict_mode: 是否严格模式（严格模式要求工具调用顺序也正确）
        allow_extra_tools: 是否允许额外的工具调用

    Example:
        >>> evaluator = ToolUsageEvaluator(strict_mode=True)
        >>> score = await evaluator.evaluate(test_case, agent_response, context)
        >>> print(f"Tool Usage F1: {score.score:.2f}")
    """

    def __init__(self, config: Dict[str, Any] | None = None, **kwargs):
        """初始化ToolUsageEvaluator

        Args:
            config: 配置字典
            **kwargs: 其他配置参数
        """
        if config is None:
            config = {}
        config.update(kwargs)

        super().__init__(config)
        self.strict_mode = self.config.get("strict_mode", False)
        self.allow_extra_tools = self.config.get("allow_extra_tools", False)

    async def evaluate(
        self,
        test_case: TestCase,
        agent_response: str,
        context: Dict[str, Any] | None = None,
    ) -> MetricScore:
        """执行工具使用评估

        Args:
            test_case: 测试用例
            agent_response: Agent响应
            context: 上下文（应包含tool_calls）

        Returns:
            MetricScore: 评估分数
        """
        context = context or {}
        tool_calls = context.get("tool_calls", [])
        expected_tools = test_case.expected_tool_calls

        # 如果没有期望的工具调用，检查是否有多余的工具调用
        if not expected_tools:
            if tool_calls and not self.allow_extra_tools:
                score = 0.5
                details = "Unexpected tool calls when none expected"
            else:
                score = 1.0
                details = "No tool usage expected or allowed"

            return MetricScore(
                name="tool_usage",
                score=score,
                weight=self.weight,
                details=details,
                metadata={
                    "precision": 1.0 if not tool_calls else 0.5,
                    "recall": 1.0,
                    "f1": score,
                    "actual_tools": [],
                    "expected_tools": [],
                },
            )

        # 提取实际调用的工具名称
        actual_tool_names = self._extract_tool_names(tool_calls)

        # 计算精确率和召回率
        correct_calls = self._count_correct_calls(actual_tool_names, expected_tools)

        precision = correct_calls / len(actual_tool_names) if actual_tool_names else 0.0
        recall = correct_calls / len(expected_tools) if expected_tools else 0.0

        # 计算F1分数
        if precision + recall > 0:
            f1 = 2 * precision * recall / (precision + recall)
        else:
            f1 = 0.0

        # 严格模式下考虑工具调用顺序
        if self.strict_mode and tool_calls and expected_tools:
            order_score = self._calculate_order_score(actual_tool_names, expected_tools)
            f1 = 0.7 * f1 + 0.3 * order_score

        return MetricScore(
            name="tool_usage",
            score=f1,
            weight=self.weight,
            details=f"Precision: {precision:.2f}, Recall: {recall:.2f}",
            metadata={
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "actual_tools": actual_tool_names,
                "expected_tools": expected_tools,
                "tool_calls_count": len(tool_calls),
                "expected_count": len(expected_tools),
            },
        )

    def _extract_tool_names(self, tool_calls: List[Dict[str, Any]]) -> List[str]:
        """从工具调用记录中提取工具名称

        Args:
            tool_calls: 工具调用记录列表

        Returns:
            List[str]: 工具名称列表
        """
        names = []
        for call in tool_calls:
            if isinstance(call, dict):
                name = call.get("name", call.get("tool", ""))
            elif hasattr(call, "name"):
                name = call.name
            else:
                name = str(call)
            if name:
                names.append(name)
        return names

    def _count_correct_calls(self, actual: List[str], expected: List[str]) -> int:
        """计算正确的工具调用数量

        Args:
            actual: 实际调用的工具列表
            expected: 期望调用的工具列表

        Returns:
            int: 正确调用的数量
        """
        expected_set = set(expected)
        return sum(1 for tool in actual if tool in expected_set)

    def _calculate_order_score(self, actual: List[str], expected: List[str]) -> float:
        """计算工具调用顺序得分

        Args:
            actual: 实际调用顺序
            expected: 期望调用顺序

        Returns:
            float: 顺序得分 (0-1)
        """
        if not expected:
            return 1.0

        # 使用最长公共子序列计算顺序相似度
        lcs_length = self._lcs_length(actual, expected)
        return lcs_length / len(expected) if expected else 1.0

    def _lcs_length(self, seq1: List[str], seq2: List[str]) -> int:
        """计算最长公共子序列长度

        Args:
            seq1: 序列1
            seq2: 序列2

        Returns:
            int: LCS长度
        """
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        return dp[m][n]
