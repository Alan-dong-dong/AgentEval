"""
自定义异常类
"""


class AgentEvalError(Exception):
    """AgentEval基础异常"""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AdapterError(AgentEvalError):
    """适配器错误

    当适配器执行失败时抛出
    """

    pass


class EvaluatorError(AgentEvalError):
    """评估器错误

    当评估器执行失败时抛出
    """

    pass


class TimeoutError(AgentEvalError):
    """超时错误

    当评估超时时抛出
    """

    pass


class ConfigurationError(AgentEvalError):
    """配置错误

    当配置无效时抛出
    """

    pass


class DatasetError(AgentEvalError):
    """数据集错误

    当数据集加载或处理失败时抛出
    """

    pass


class ValidationError(AgentEvalError):
    """验证错误

    当输入验证失败时抛出
    """

    pass
