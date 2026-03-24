"""
功能正确性评估器
"""

from typing import Any, Dict

from agenteval.evaluators.base import LLMBasedEvaluator
from agenteval.models.task import TestCase
from agenteval.models.result import MetricScore


class CorrectnessEvaluator(LLMBasedEvaluator):
    """功能正确性评估器

    评估Agent是否正确理解并完成了用户请求的任务。
    使用LLM作为评判，分析Agent输出的正确性。

    Attributes:
        threshold: 通过阈值 (默认: 0.7)
        strict_mode: 是否严格模式

    Example:
        >>> evaluator = CorrectnessEvaluator(model="gpt-4", threshold=0.8)
        >>> score = await evaluator.evaluate(test_case, agent_response, context)
        >>> print(f"Correctness: {score.score:.2f}")
    """

    SYSTEM_PROMPT = """你是一个AI Agent输出质量评估专家。
你的任务是评估Agent的响应是否正确完成了用户的请求。
请客观、准确地评估，不要过于宽松或过于严格。"""

    EVALUATION_PROMPT = """请评估以下Agent响应的正确性。

## 用户请求
{input_message}

## Agent响应
{agent_response}

## 期望输出（如有）
{expected_output}

## 评估标准
1. 任务理解准确性（是否正确理解用户意图）- 25%
2. 输出完整性（是否完整回答了问题）- 25%
3. 信息准确性（提供的信息是否正确）- 25%
4. 逻辑一致性（推理过程是否合理）- 25%

请给出0-100的分数，并简要说明理由。

输出格式：
分数: <0-100的整数>
理由: <简要说明>"""

    def __init__(self, config: Dict[str, Any] | None = None, **kwargs):
        """初始化CorrectnessEvaluator

        Args:
            config: 配置字典
            **kwargs: 其他配置参数
        """
        if config is None:
            config = {}
        config.update(kwargs)

        super().__init__(config)
        self.threshold = self.config.get("threshold", 0.7)
        self.strict_mode = self.config.get("strict_mode", False)

    async def evaluate(
        self,
        test_case: TestCase,
        agent_response: str,
        context: Dict[str, Any] | None = None,
    ) -> MetricScore:
        """执行正确性评估

        Args:
            test_case: 测试用例
            agent_response: Agent响应
            context: 上下文

        Returns:
            MetricScore: 评估分数
        """
        # 如果有期望输出，使用LLM评估
        if test_case.expected_output:
            prompt = self.EVALUATION_PROMPT.format(
                input_message=test_case.input_message,
                agent_response=agent_response,
                expected_output=test_case.expected_output,
            )

            try:
                llm_response = await self._call_llm(
                    prompt=prompt,
                    system_prompt=self.SYSTEM_PROMPT,
                )
                score = self._parse_score_from_response(llm_response)
            except Exception as e:
                score = 0.5
                llm_response = f"LLM call failed: {str(e)}"
        else:
            # 没有期望输出时，检查响应是否为空或过于简短
            if not agent_response or len(agent_response.strip()) < 10:
                score = 0.3
                llm_response = "Response is empty or too short"
            else:
                score = 0.7
                llm_response = "No expected output provided, giving default score"

        return MetricScore(
            name="correctness",
            score=score,
            weight=self.weight,
            details=llm_response if test_case.expected_output else "Basic check only",
            metadata={
                "threshold": self.threshold,
                "passed": score >= self.threshold,
                "strict_mode": self.strict_mode,
            },
        )
