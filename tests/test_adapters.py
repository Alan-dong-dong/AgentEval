"""
适配器测试
"""

import pytest
from agenteval.adapters.base import (
    AgentResponse,
    CallableAdapter,
    get_adapter_class,
    register_adapter,
)
from agenteval.models.task import AgentConfig


class TestAgentResponse:
    """AgentResponse测试"""

    def test_create_agent_response(self):
        """测试创建AgentResponse"""
        response = AgentResponse(
            content="Hello",
            tool_calls=[{"name": "test", "input": {}}],
            metadata={"key": "value"},
        )

        assert response.content == "Hello"
        assert len(response.tool_calls) == 1
        assert response.metadata["key"] == "value"

    def test_default_agent_response(self):
        """测试默认AgentResponse"""
        response = AgentResponse()

        assert response.content == ""
        assert response.tool_calls == []
        assert response.metadata == {}


class TestCallableAdapter:
    """CallableAdapter测试"""

    @pytest.mark.asyncio
    async def test_callable_function(self):
        """测试Callable函数"""

        def my_agent(prompt: str) -> str:
            return f"Response to: {prompt}"

        config = AgentConfig(
            framework="callable",
            agent_callable=my_agent,
        )
        adapter = CallableAdapter(config)

        response = await adapter.run_single_turn("Hello")
        assert "Response to: Hello" in response.content

    @pytest.mark.asyncio
    async def test_callable_class(self):
        """测试Callable类"""

        class MyAgent:
            def __call__(self, prompt: str) -> str:
                return "Class response"

        config = AgentConfig(
            framework="callable",
            agent_instance=MyAgent(),
        )
        adapter = CallableAdapter(config)

        response = await adapter.run_single_turn("Hello")
        assert response.content == "Class response"

    @pytest.mark.asyncio
    async def test_async_callable(self):
        """测试异步Callable"""

        async def async_agent(prompt: str) -> str:
            return "Async response"

        config = AgentConfig(
            framework="callable",
            agent_callable=async_agent,
        )
        adapter = CallableAdapter(config)

        response = await adapter.run_single_turn("Hello")
        assert response.content == "Async response"

    def test_adapter_info(self):
        """测试适配器信息"""
        config = AgentConfig(
            framework="callable",
            agent_callable=lambda x: "test",
        )
        adapter = CallableAdapter(config)

        info = adapter.get_framework_info()
        assert info["name"] == "callable"


class TestAdapterRegistry:
    """适配器注册表测试"""

    def test_get_adapter_class(self):
        """测试获取适配器类"""
        adapter_class = get_adapter_class("callable")
        assert adapter_class == CallableAdapter

    def test_register_adapter(self):
        """测试注册适配器"""

        class CustomAdapter(CallableAdapter):
            FRAMEWORK_NAME = "custom"

        register_adapter("custom", CustomAdapter)
        adapter_class = get_adapter_class("custom")
        assert adapter_class == CustomAdapter
