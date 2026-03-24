"""
核心评估引擎
"""

import asyncio
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from agenteval.models.task import TestCase, AgentConfig
from agenteval.models.result import EvaluationResult, BenchmarkResult, MetricScore
from agenteval.evaluators.base import BaseEvaluator
from agenteval.evaluators.correctness import CorrectnessEvaluator
from agenteval.evaluators.efficiency import EfficiencyEvaluator
from agenteval.adapters.base import (
    BaseAdapter,
    AgentResponse,
    CallableAdapter,
    get_adapter_class,
)
from agenteval.exceptions import AdapterError, EvaluatorError, TimeoutError


class EvaluationEngine:
    """评估引擎

    负责编排整个评估流程，包括：
    - 管理评估器和适配器
    - 执行单个和批量评估
    - 控制并发执行
    - 聚合评估结果

    Attributes:
        config: 引擎配置
        evaluators: 评估器列表
        adapter: 框架适配器
        results: 评估结果列表

    Example:
        >>> engine = EvaluationEngine()
        >>> engine.add_evaluator(CorrectnessEvaluator())
        >>> engine.set_adapter(my_adapter)
        >>> result = await engine.evaluate_single(test_case)
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        """初始化评估引擎

        Args:
            config: 引擎配置
                - max_concurrency: 最大并发数 (默认: 5)
                - timeout: 单次评估超时秒数 (默认: 30)
                - retry_count: 失败重试次数 (默认: 3)
                - log_level: 日志级别 (默认: "INFO")
        """
        self.config = config or {}
        self.evaluators: List[BaseEvaluator] = []
        self.adapter: Optional[BaseAdapter] = None
        self.results: List[EvaluationResult] = []

        # 并发控制
        self.max_concurrency = self.config.get("max_concurrency", 5)
        self.timeout = self.config.get("timeout", 30)
        self.retry_count = self.config.get("retry_count", 3)

        # 信号量
        self._semaphore = asyncio.Semaphore(self.max_concurrency)

    def set_adapter(self, adapter: BaseAdapter):
        """设置框架适配器

        Args:
            adapter: 框架适配器实例
        """
        self.adapter = adapter

    def add_evaluator(self, evaluator: BaseEvaluator):
        """添加评估器

        Args:
            evaluator: 评估器实例
        """
        self.evaluators.append(evaluator)

    def add_evaluators(self, evaluators: List[BaseEvaluator]):
        """批量添加评估器

        Args:
            evaluators: 评估器列表
        """
        self.evaluators.extend(evaluators)

    def get_results(self) -> List[EvaluationResult]:
        """获取所有评估结果

        Returns:
            List[EvaluationResult]: 评估结果列表
        """
        return self.results.copy()

    def clear_results(self):
        """清空评估结果"""
        self.results.clear()

    async def evaluate_single(
        self,
        test_case: TestCase,
        context: Dict[str, Any] | None = None,
    ) -> EvaluationResult:
        """执行单个测试用例评估

        Args:
            test_case: 测试用例
            context: 额外上下文信息

        Returns:
            EvaluationResult: 评估结果

        Raises:
            AdapterError: 适配器未设置或执行失败
            TimeoutError: 评估超时
        """
        if self.adapter is None:
            raise AdapterError("No adapter set. Call set_adapter() first.")

        start_time = time.time()
        context = context or {}

        try:
            # 执行Agent
            agent_response = await asyncio.wait_for(
                self._run_agent(test_case, context),
                timeout=self.timeout,
            )

            latency_ms = (time.time() - start_time) * 1000

            # 更新上下文
            context.update(
                {
                    "latency_ms": latency_ms,
                    "tool_calls": agent_response.tool_calls,
                    "agent_metadata": agent_response.metadata,
                }
            )

            # 执行所有评估器
            scores = await self._run_evaluators(test_case, agent_response, context)

            # 计算总体分数
            overall_score = self._calculate_overall_score(scores)

            result = EvaluationResult(
                test_case_id=test_case.id,
                agent_response=agent_response.content,
                tool_calls=agent_response.tool_calls,
                scores=scores,
                overall_score=overall_score,
                latency_ms=latency_ms,
                success=True,
                timestamp=datetime.now(),
            )

            self.results.append(result)
            return result

        except asyncio.TimeoutError:
            result = EvaluationResult(
                test_case_id=test_case.id,
                success=False,
                error_message=f"Evaluation timed out after {self.timeout}s",
                timestamp=datetime.now(),
            )
            self.results.append(result)
            return result

        except Exception as e:
            result = EvaluationResult(
                test_case_id=test_case.id,
                success=False,
                error_message=str(e),
                timestamp=datetime.now(),
            )
            self.results.append(result)
            return result

    async def evaluate_batch(
        self,
        test_cases: List[TestCase],
        context: Dict[str, Any] | None = None,
    ) -> BenchmarkResult:
        """批量执行评估

        Args:
            test_cases: 测试用例列表
            context: 额外上下文信息

        Returns:
            BenchmarkResult: 基准测试结果
        """
        benchmark_id = str(uuid.uuid4())
        start_time = datetime.now()

        # 并发执行评估
        tasks = []
        for test_case in test_cases:
            task = self._evaluate_with_semaphore(test_case, context)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常结果
        eval_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                eval_results.append(
                    EvaluationResult(
                        test_case_id=test_cases[i].id,
                        success=False,
                        error_message=str(result),
                        timestamp=datetime.now(),
                    )
                )
            else:
                eval_results.append(result)

        self.results.extend(eval_results)

        end_time = datetime.now()

        # 聚合结果
        benchmark_result = self._aggregate_results(
            benchmark_id=benchmark_id,
            results=eval_results,
            start_time=start_time,
            end_time=end_time,
        )

        return benchmark_result

    async def _run_agent(
        self, test_case: TestCase, context: Dict[str, Any]
    ) -> AgentResponse:
        """运行Agent

        Args:
            test_case: 测试用例
            context: 上下文

        Returns:
            AgentResponse: Agent响应
        """
        if test_case.conversation_history:
            # 多轮对话模式
            messages = test_case.conversation_history + [
                {"role": "user", "content": test_case.input_message}
            ]
            return await self.adapter.run_multi_turn(
                messages=messages,
                context=test_case.context,
                tools=test_case.tools,
            )
        else:
            # 单轮对话模式
            return await self.adapter.run_single_turn(
                message=test_case.input_message,
                context=test_case.context,
                tools=test_case.tools,
            )

    async def _run_evaluators(
        self,
        test_case: TestCase,
        agent_response: AgentResponse,
        context: Dict[str, Any],
    ) -> List[MetricScore]:
        """运行所有评估器

        Args:
            test_case: 测试用例
            agent_response: Agent响应
            context: 上下文

        Returns:
            List[MetricScore]: 评分列表
        """
        scores = []

        for evaluator in self.evaluators:
            try:
                score = await evaluator.evaluate(
                    test_case=test_case,
                    agent_response=agent_response.content,
                    context=context,
                )
                scores.append(score)
            except Exception as e:
                # 评估器失败时使用默认分数
                scores.append(
                    MetricScore(
                        name=evaluator.name,
                        score=0.0,
                        weight=evaluator.weight,
                        details=f"Evaluator failed: {str(e)}",
                    )
                )

        return scores

    async def _evaluate_with_semaphore(
        self,
        test_case: TestCase,
        context: Dict[str, Any] | None = None,
    ) -> EvaluationResult:
        """带信号量控制的评估

        Args:
            test_case: 测试用例
            context: 上下文

        Returns:
            EvaluationResult: 评估结果
        """
        async with self._semaphore:
            return await self.evaluate_single(test_case, context)

    def _calculate_overall_score(self, scores: List[MetricScore]) -> float:
        """计算加权总体分数

        Args:
            scores: 评分列表

        Returns:
            float: 综合分数
        """
        if not scores:
            return 0.0

        total_weight = sum(s.weight for s in scores)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(s.score * s.weight for s in scores)
        return weighted_sum / total_weight

    def _aggregate_results(
        self,
        benchmark_id: str,
        results: List[EvaluationResult],
        start_time: datetime,
        end_time: datetime,
    ) -> BenchmarkResult:
        """聚合评估结果

        Args:
            benchmark_id: 基准测试ID
            results: 评估结果列表
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            BenchmarkResult: 基准测试结果
        """
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]

        # 计算平均分数
        avg_score = (
            sum(r.overall_score for r in successful_results) / len(successful_results)
            if successful_results
            else 0.0
        )

        # 计算各维度分数
        dimension_scores = {}
        if successful_results:
            all_dimensions = set()
            for r in successful_results:
                for s in r.scores:
                    all_dimensions.add(s.name)

            for dim in all_dimensions:
                dim_scores = [
                    s.score
                    for r in successful_results
                    for s in r.scores
                    if s.name == dim
                ]
                dimension_scores[dim] = (
                    sum(dim_scores) / len(dim_scores) if dim_scores else 0.0
                )

        # 性能统计
        latencies = [r.latency_ms for r in successful_results]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

        return BenchmarkResult(
            id=benchmark_id,
            name=f"Benchmark_{benchmark_id[:8]}",
            results=results,
            total_tests=len(results),
            passed_tests=len(successful_results),
            failed_tests=len(failed_results),
            average_score=avg_score,
            dimension_scores=dimension_scores,
            avg_latency_ms=avg_latency,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=(end_time - start_time).total_seconds(),
        )
