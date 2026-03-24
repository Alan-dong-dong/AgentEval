"""
工具函数模块
"""

import logging
from typing import Any, Dict


def setup_logging(level: str = "INFO") -> logging.Logger:
    """设置日志

    Args:
        level: 日志级别

    Returns:
        logging.Logger: 日志器实例
    """
    logger = logging.getLogger("agenteval")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)

    return logger


def merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """深度合并字典

    Args:
        base: 基础字典
        override: 覆盖字典

    Returns:
        Dict: 合并后的字典
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result
