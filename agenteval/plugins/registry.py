"""
插件注册系统
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Type


@dataclass
class PluginInfo:
    """插件信息

    Attributes:
        name: 插件名称
        version: 版本号
        description: 描述
        author: 作者
        plugin_type: 插件类型 (evaluator, adapter, dataset)
        entry_point: 入口点
    """

    name: str
    version: str
    description: str
    author: str
    plugin_type: str
    entry_point: str


class PluginRegistry:
    """插件注册表

    管理所有注册的插件，包括评估器、适配器和数据集。

    Example:
        >>> registry = PluginRegistry()
        >>> registry.register_evaluator("my_eval", MyEvaluator)
        >>> evaluator_class = registry.get_evaluator("my_eval")
    """

    def __init__(self):
        self._evaluators: Dict[str, Type] = {}
        self._adapters: Dict[str, Type] = {}
        self._datasets: Dict[str, Any] = {}
        self._plugins_info: Dict[str, PluginInfo] = {}

    def register_evaluator(
        self,
        name: str,
        evaluator_class: Type,
        info: PluginInfo | None = None,
    ):
        """注册评估器插件

        Args:
            name: 评估器名称
            evaluator_class: 评估器类
            info: 插件信息（可选）
        """
        self._evaluators[name] = evaluator_class
        if info:
            self._plugins_info[name] = info

    def register_adapter(
        self,
        name: str,
        adapter_class: Type,
        info: PluginInfo | None = None,
    ):
        """注册适配器插件

        Args:
            name: 适配器名称
            adapter_class: 适配器类
            info: 插件信息（可选）
        """
        self._adapters[name] = adapter_class
        if info:
            self._plugins_info[name] = info

    def register_dataset(
        self,
        name: str,
        dataset: Any,
        info: PluginInfo | None = None,
    ):
        """注册数据集插件

        Args:
            name: 数据集名称
            dataset: 数据集
            info: 插件信息（可选）
        """
        self._datasets[name] = dataset
        if info:
            self._plugins_info[name] = info

    def get_evaluator(self, name: str) -> Type | None:
        """获取评估器类

        Args:
            name: 评估器名称

        Returns:
            Optional[Type]: 评估器类
        """
        return self._evaluators.get(name)

    def get_adapter(self, name: str) -> Type | None:
        """获取适配器类

        Args:
            name: 适配器名称

        Returns:
            Optional[Type]: 适配器类
        """
        return self._adapters.get(name)

    def get_dataset(self, name: str) -> Any | None:
        """获取数据集

        Args:
            name: 数据集名称

        Returns:
            Optional[Any]: 数据集
        """
        return self._datasets.get(name)

    def list_evaluators(self) -> List[str]:
        """列出所有注册的评估器

        Returns:
            List[str]: 评估器名称列表
        """
        return list(self._evaluators.keys())

    def list_adapters(self) -> List[str]:
        """列出所有注册的适配器

        Returns:
            List[str]: 适配器名称列表
        """
        return list(self._adapters.keys())

    def list_datasets(self) -> List[str]:
        """列出所有注册的数据集

        Returns:
            List[str]: 数据集名称列表
        """
        return list(self._datasets.keys())

    def list_plugins(self) -> List[PluginInfo]:
        """列出所有插件信息

        Returns:
            List[PluginInfo]: 插件信息列表
        """
        return list(self._plugins_info.values())

    def discover_plugins(self, package_name: str = "agenteval_plugins"):
        """自动发现插件

        从指定包中自动发现并注册插件。

        Args:
            package_name: 插件包名称
        """
        try:
            import importlib
            import pkgutil

            package = importlib.import_module(package_name)
            for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
                module = importlib.import_module(f"{package_name}.{name}")
                if hasattr(module, "register"):
                    module.register(self)
        except ImportError:
            pass


# 全局插件注册表
_registry = PluginRegistry()


def get_registry() -> PluginRegistry:
    """获取全局插件注册表

    Returns:
        PluginRegistry: 插件注册表实例
    """
    return _registry


def register_evaluator(name: str, evaluator_class: Type | None = None):
    """注册评估器装饰器

    Args:
        name: 评估器名称
        evaluator_class: 评估器类（可选，用于直接注册）

    Returns:
        装饰器函数或评估器类

    Example:
        >>> @register_evaluator("my_evaluator")
        ... class MyEvaluator(BaseEvaluator):
        ...     pass
    """

    def decorator(cls):
        _registry.register_evaluator(name, cls)
        return cls

    if evaluator_class is not None:
        # 直接注册模式
        _registry.register_evaluator(name, evaluator_class)
        return evaluator_class
    return decorator


def register_adapter(name: str, adapter_class: Type | None = None):
    """注册适配器装饰器

    Args:
        name: 适配器名称
        adapter_class: 适配器类（可选，用于直接注册）

    Returns:
        装饰器函数或适配器类

    Example:
        >>> @register_adapter("my_adapter")
        ... class MyAdapter(BaseAdapter):
        ...     pass
    """

    def decorator(cls):
        _registry.register_adapter(name, cls)
        return cls

    if adapter_class is not None:
        # 直接注册模式
        _registry.register_adapter(name, adapter_class)
        return adapter_class
    return decorator
