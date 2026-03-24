"""
适配器基类
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, List, Optional

from agenteval.models.task import AgentConfig
from agenteval.exceptions import AdapterError


@dataclass
class AgentResponse:
    """Agent响应封装

    Attributes:
        content: 响应文本内容
        tool_calls: 工具调用记录列表
        metadata: 额外元数据
    """

    content: str = ""
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAdapter(ABC):
    """框架适配器基类

    所有框架适配器必须继承此类并实现核心方法。

    Attributes:
        FRAMEWORK_NAME: 框架名称标识
        agent_config: Agent配置

    Example:
        >>> class MyAdapter(BaseAdapter):
        ...     FRAMEWORK_NAME = "my_framework"
        ...
        ...     async def run_single_turn(self, message, context=None, tools=None):
        ...         response = await my_agent.arun(message)
        ...         return AgentResponse(content=response)
    """

    FRAMEWORK_NAME: str = "base"

    def __init__(self, agent_config: AgentConfig):
        """初始化适配器

        Args:
            agent_config: Agent配置对象
        """
        self.agent_config = agent_config
        self._validate_config()

    def _validate_config(self):
        """验证配置是否有效

        Raises:
            AdapterError: 配置无效时抛出
        """
        if (
            self.agent_config.agent_instance is None
            and self.agent_config.agent_callable is None
        ):
            raise AdapterError(
                "Either agent_instance or agent_callable must be provided"
            )

    @abstractmethod
    async def run_single_turn(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Any]] = None,
    ) -> AgentResponse:
        """执行单轮对话

        Args:
            message: 用户消息
            context: 上下文信息
            tools: 可用工具列表

        Returns:
            AgentResponse: Agent的响应
        """
        pass

    async def run_multi_turn(
        self,
        messages: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Any]] = None,
    ) -> AgentResponse:
        """执行多轮对话

        默认实现：只处理最后一条消息

        Args:
            messages: 消息历史列表 [{"role": "user", "content": "..."}]
            context: 上下文信息
            tools: 可用工具列表

        Returns:
            AgentResponse: Agent的响应
        """
        if not messages:
            return AgentResponse(content="")

        last_message = messages[-1].get("content", "")
        return await self.run_single_turn(last_message, context, tools)

    async def run_streaming(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """流式响应

        默认实现：非流式返回

        Args:
            message: 用户消息
            context: 上下文信息

        Yields:
            str: 响应内容块
        """
        response = await self.run_single_turn(message, context)
        yield response.content

    def get_framework_info(self) -> Dict[str, Any]:
        """获取框架信息

        Returns:
            Dict: 框架信息
        """
        return {
            "name": self.FRAMEWORK_NAME,
            "version": "1.0.0",
            "supported_features": ["single_turn", "multi_turn"],
        }

    @classmethod
    def supports_framework(cls, framework_name: str) -> bool:
        """检查是否支持指定框架

        Args:
            framework_name: 框架名称

        Returns:
            bool: 是否支持
        """
        return cls.FRAMEWORK_NAME.lower() == framework_name.lower()


class CallableAdapter(BaseAdapter):
    """通用Callable适配器

    支持任何可调用对象（函数、类实例等）作为Agent。

    Example:
        >>> def my_agent(prompt: str) -> str:
        ...     return "Hello, world!"
        ...
        >>> config = AgentConfig(framework="callable", agent_callable=my_agent)
        >>> adapter = CallableAdapter(config)
        >>> response = await adapter.run_single_turn("Hi")
        >>> print(response.content)
    """

    FRAMEWORK_NAME = "callable"

    async def run_single_turn(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Any]] = None,
    ) -> AgentResponse:
        """执行单轮对话

        Args:
            message: 用户消息
            context: 上下文信息
            tools: 可用工具列表

        Returns:
            AgentResponse: Agent的响应
        """
        try:
            agent = self.agent_config.agent_callable or self.agent_config.agent_instance

            if agent is None:
                raise AdapterError("No agent callable or instance provided")

            # 检查是否是异步函数
            import asyncio
            import inspect

            if inspect.iscoroutinefunction(agent):
                response = await agent(message)
            elif callable(agent):
                # 使用asyncio.to_thread包装同步调用
                response = await asyncio.to_thread(agent, message)
            else:
                raise AdapterError(f"Agent is not callable: {type(agent)}")

            return AgentResponse(
                content=str(response),
                metadata={"framework": self.FRAMEWORK_NAME},
            )

        except Exception as e:
            if isinstance(e, AdapterError):
                raise
            raise AdapterError(f"Agent execution failed: {str(e)}")


class LangChainAdapter(BaseAdapter):
    """LangChain框架适配器

    支持LangChain Agent、AgentExecutor和Runnable接口。

    Example:
        >>> from langchain.agents import AgentExecutor
        >>> config = AgentConfig(
        ...     framework="langchain",
        ...     agent_instance=my_agent_executor
        ... )
        >>> adapter = LangChainAdapter(config)
    """

    FRAMEWORK_NAME = "langchain"

    async def run_single_turn(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Any]] = None,
    ) -> AgentResponse:
        """执行单轮对话

        Args:
            message: 用户消息
            context: 上下文信息
            tools: 可用工具列表

        Returns:
            AgentResponse: Agent的响应
        """
        import asyncio

        agent = self.agent_config.agent_instance

        try:
            # 支持不同类型的LangChain Agent
            if hasattr(agent, "ainvoke"):
                # LangChain Runnable接口
                result = await agent.ainvoke({"input": message})
                content = result.get("output", str(result))
                tool_calls = self._extract_tool_calls(result)
            elif hasattr(agent, "arun"):
                # 旧版Agent接口
                content = await agent.arun(message)
                tool_calls = []
            elif hasattr(agent, "run"):
                # 同步接口
                content = await asyncio.to_thread(agent.run, message)
                tool_calls = []
            else:
                raise AdapterError(f"Unsupported LangChain agent type: {type(agent)}")

            return AgentResponse(
                content=str(content),
                tool_calls=tool_calls,
                metadata={"framework": self.FRAMEWORK_NAME},
            )

        except Exception as e:
            if isinstance(e, AdapterError):
                raise
            raise AdapterError(f"LangChain agent execution failed: {str(e)}")

    def _extract_tool_calls(self, result: Any) -> List[Dict[str, Any]]:
        """提取工具调用信息

        Args:
            result: Agent执行结果

        Returns:
            List[Dict]: 工具调用记录列表
        """
        tool_calls = []

        if isinstance(result, dict):
            intermediate_steps = result.get("intermediate_steps", [])
            for step in intermediate_steps:
                if isinstance(step, tuple) and len(step) >= 2:
                    action, observation = step[0], step[1]
                    tool_calls.append(
                        {
                            "name": getattr(action, "tool", "unknown"),
                            "input": getattr(action, "tool_input", {}),
                            "output": str(observation),
                        }
                    )

        return tool_calls


ADAPTER_REGISTRY: Dict[str, type[BaseAdapter]] = {
    "callable": CallableAdapter,
    "langchain": LangChainAdapter,
}


def get_adapter_class(framework: str) -> type[BaseAdapter]:
    """获取适配器类

    Args:
        framework: 框架名称

    Returns:
        Type[BaseAdapter]: 适配器类

    Raises:
        AdapterError: 不支持的框架时抛出
    """
    framework = framework.lower()
    if framework not in ADAPTER_REGISTRY:
        raise AdapterError(
            f"Unsupported framework: {framework}. "
            f"Supported: {list(ADAPTER_REGISTRY.keys())}"
        )
    return ADAPTER_REGISTRY[framework]


def register_adapter(name: str, adapter_class: type[BaseAdapter]):
    """注册适配器

    Args:
        name: 适配器名称
        adapter_class: 适配器类
    """
    ADAPTER_REGISTRY[name.lower()] = adapter_class
