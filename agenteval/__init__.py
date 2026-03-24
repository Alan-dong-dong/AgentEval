"""
AgentEval - 专为AI Agent设计的开源评估框架

让Agent评估变得简单、可靠、可复现。

Example:
    >>> from agenteval import quick_eval
    >>> result = quick_eval(my_agent, "What is 2+2?", expected="4")
    >>> print(f"Score: {result['score']:.2f}")
"""

__version__ = "0.1.0"
__author__ = "AgentEval Team"
__license__ = "MIT"

# 核心组件
from agenteval.core.engine import EvaluationEngine

# 简单模式API
from agenteval.simple.quick_eval import quick_eval

# 数据模型
from agenteval.models.task import (
    TestCase,
    ToolDefinition,
    TaskType,
    TaskDifficulty,
    AgentConfig,
)
from agenteval.models.result import (
    EvaluationResult,
    BenchmarkResult,
    MetricScore,
)

# 评估器
from agenteval.evaluators.base import (
    BaseEvaluator,
    LLMBasedEvaluator,
    RuleBasedEvaluator,
)
from agenteval.evaluators.correctness import CorrectnessEvaluator
from agenteval.evaluators.tool_usage import ToolUsageEvaluator
from agenteval.evaluators.efficiency import EfficiencyEvaluator

# 适配器
from agenteval.adapters.base import BaseAdapter, AgentResponse

# 异常
from agenteval.exceptions import (
    AgentEvalError,
    AdapterError,
    EvaluatorError,
    TimeoutError,
    ConfigurationError,
)


__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    "__license__",
    # 核心组件
    "EvaluationEngine",
    # 简单模式API
    "quick_eval",
    # 数据模型
    "TestCase",
    "ToolDefinition",
    "TaskType",
    "TaskDifficulty",
    "AgentConfig",
    "EvaluationResult",
    "BenchmarkResult",
    "MetricScore",
    # 评估器
    "BaseEvaluator",
    "LLMBasedEvaluator",
    "RuleBasedEvaluator",
    "CorrectnessEvaluator",
    "ToolUsageEvaluator",
    "EfficiencyEvaluator",
    # 适配器
    "BaseAdapter",
    "AgentResponse",
    # 异常
    "AgentEvalError",
    "AdapterError",
    "EvaluatorError",
    "TimeoutError",
    "ConfigurationError",
]
