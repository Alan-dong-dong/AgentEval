"""
评估结果数据模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class MetricScore:
    """单项指标评分

    Attributes:
        name: 评估器名称
        score: 评分 (0-1)
        weight: 权重
        details: 详细说明
        metadata: 元数据
    """

    name: str = ""
    score: float = 0.0
    weight: float = 1.0
    details: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "score": self.score,
            "weight": self.weight,
            "details": self.details,
            "metadata": self.metadata,
        }


@dataclass
class EvaluationResult:
    """单次评估结果

    Attributes:
        test_case_id: 测试用例ID
        agent_response: Agent响应内容
        tool_calls: 工具调用记录
        scores: 评分明细列表
        overall_score: 综合分数
        latency_ms: 响应延迟(毫秒)
        token_usage: Token使用统计
        success: 是否成功执行
        error_message: 错误信息
        timestamp: 评估时间戳
        details: 额外详细信息
    """

    test_case_id: str = ""
    agent_response: str = ""
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    scores: List[MetricScore] = field(default_factory=list)
    overall_score: float = 0.0
    latency_ms: float = 0.0
    token_usage: Dict[str, int] = field(default_factory=dict)
    success: bool = True
    error_message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "test_case_id": self.test_case_id,
            "agent_response": self.agent_response,
            "tool_calls": self.tool_calls,
            "scores": [s.to_dict() for s in self.scores],
            "overall_score": self.overall_score,
            "latency_ms": self.latency_ms,
            "token_usage": self.token_usage,
            "success": self.success,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


@dataclass
class BenchmarkResult:
    """基准测试结果

    Attributes:
        id: 基准测试唯一标识
        name: 基准测试名称
        agent_config: Agent配置信息
        results: 所有评估结果列表
        total_tests: 总测试数
        passed_tests: 通过测试数
        failed_tests: 失败测试数
        average_score: 平均分数
        dimension_scores: 各维度分数统计
        avg_latency_ms: 平均延迟
        total_tokens: 总Token消耗
        duration_seconds: 总耗时
        start_time: 开始时间
        end_time: 结束时间
    """

    id: str = ""
    name: str = ""
    agent_config: Dict[str, Any] = field(default_factory=dict)
    results: List[EvaluationResult] = field(default_factory=list)
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    average_score: float = 0.0
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    avg_latency_ms: float = 0.0
    total_tokens: int = 0
    duration_seconds: float = 0.0
    start_time: datetime | None = None
    end_time: datetime | None = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "agent_config": self.agent_config,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "average_score": self.average_score,
            "dimension_scores": self.dimension_scores,
            "avg_latency_ms": self.avg_latency_ms,
            "total_tokens": self.total_tokens,
            "duration_seconds": self.duration_seconds,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "results": [r.to_dict() for r in self.results],
        }

    def summary(self) -> str:
        """生成文本摘要"""
        lines = [
            "=" * 50,
            f"Benchmark: {self.name}",
            "=" * 50,
            f"Total Tests: {self.total_tests}",
            f"Passed: {self.passed_tests}",
            f"Failed: {self.failed_tests}",
            f"Average Score: {self.average_score:.2f}",
            f"Duration: {self.duration_seconds:.2f}s",
            "-" * 50,
            "Dimension Scores:",
        ]
        for dim, score in self.dimension_scores.items():
            bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
            lines.append(f"  {dim}: {score:.2f} {bar}")
        lines.append("=" * 50)
        return "\n".join(lines)
