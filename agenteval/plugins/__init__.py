"""
插件模块
"""

from agenteval.plugins.registry import (
    PluginRegistry,
    PluginInfo,
    get_registry,
    register_evaluator,
    register_adapter,
)

__all__ = [
    "PluginRegistry",
    "PluginInfo",
    "get_registry",
    "register_evaluator",
    "register_adapter",
]
