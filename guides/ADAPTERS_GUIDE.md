# 适配器开发指南 🔌

## 目录

- [概述](#概述)
- [内置适配器](#内置适配器)
- [适配器接口](#适配器接口)
- [自定义适配器](#自定义适配器)
- [插件注册](#插件注册)
- [最佳实践](#最佳实践)

---

## 概述

适配器是AgentEval的桥梁组件，负责将不同框架的Agent统一到标准化接口上。通过适配器模式，AgentEval可以支持任意Agent框架。

### 设计原则

- **统一接口**：所有适配器实现相同接口
- **框架无关**：屏蔽底层框架差异
- **可扩展**：支持自定义适配器
- **自动发现**：支持插件机制

---

## 内置适配器

### LangChainAdapter

支持LangChain Agent和LangGraph。

```python
from agenteval.adapters import LangChainAdapter
from agenteval.models import AgentConfig

# 配置Agent
config = AgentConfig(
    framework="langchain",
    agent_instance=my_langchain_agent
)

# 创建适配器
adapter = LangChainAdapter(config)
```

**支持的Agent类型：**
- AgentExecutor
- RunnableSequence
- LangGraph

**示例：**

```python
from langchain.agents import AgentExecutor, create_openai_agent
from langchain_openai import ChatOpenAI
from agenteval.adapters import LangChainAdapter
from agenteval.models import AgentConfig

# 创建LangChain Agent
llm = ChatOpenAI(model="gpt-4")
agent = create_openai_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# 配置适配器
config = AgentConfig(
    framework="langchain",
    agent_instance=agent_executor
)
adapter = LangChainAdapter(config)

# 执行
response = await adapter.run_single_turn("What is 2+2?")
print(response.content)
```

---

### CrewAIAdapter

支持CrewAI多Agent系统。

```python
from agenteval.adapters import CrewAIAdapter
from agenteval.models import AgentConfig

config = AgentConfig(
    framework="crewai",
    agent_instance=my_crew
)
adapter = CrewAIAdapter(config)
```

**示例：**

```python
from crewai import Agent, Task, Crew
from agenteval.adapters import CrewAIAdapter
from agenteval.models import AgentConfig

# 创建CrewAI Agent
researcher = Agent(
    role="Researcher",
    goal="Research topics thoroughly",
    backstory="You are an expert researcher"
)

writer = Agent(
    role="Writer",
    goal="Write clear summaries",
    backstory="You are a skilled writer"
)

crew = Crew(agents=[researcher, writer])

# 配置适配器
config = AgentConfig(
    framework="crewai",
    agent_instance=crew
)
adapter = CrewAIAdapter(config)
```

---

### AutoGenAdapter

支持AutoGen多Agent对话系统。

```python
from agenteval.adapters import AutoGenAdapter
from agenteval.models import AgentConfig

config = AgentConfig(
    framework="autogen",
    agent_instance=my_autogen_agent
)
adapter = AutoGenAdapter(config)
```

**示例：**

```python
import autogen
from agenteval.adapters import AutoGenAdapter
from agenteval.models import AgentConfig

# 创建AutoGen Agent
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={"model": "gpt-4"}
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER"
)

# 配置适配器
config = AgentConfig(
    framework="autogen",
    agent_instance=assistant
)
adapter = AutoGenAdapter(config)
```

---

### CallableAdapter

通用Callable接口适配器，支持任何可调用对象。

```python
from agenteval.adapters import CallableAdapter
from agenteval.models import AgentConfig

# 使用函数
def my_agent(prompt: str) -> str:
    return "The answer is 42"

config = AgentConfig(
    framework="callable",
    agent_callable=my_agent
)
adapter = CallableAdapter(config)

# 使用类
class MyAgent:
    def __call__(self, prompt: str) -> str:
        return "The answer is 42"

config = AgentConfig(
    framework="callable",
    agent_instance=MyAgent()
)
adapter = CallableAdapter(config)
```

---

## 适配器接口

### BaseAdapter

所有适配器必须继承BaseAdapter并实现其接口。

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from agenteval.adapters.base import AgentResponse

class BaseAdapter(ABC):
    """框架适配器基类"""
    
    FRAMEWORK_NAME: str = "base"
    
    def __init__(self, agent_config):
        self.agent_config = agent_config
        self._validate_config()
    
    def _validate_config(self):
        """验证配置"""
        pass
    
    @abstractmethod
    async def run_single_turn(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Any]] = None
    ) -> AgentResponse:
        """执行单轮对话"""
        pass
    
    @abstractmethod
    async def run_multi_turn(
        self,
        messages: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Any]] = None
    ) -> AgentResponse:
        """执行多轮对话"""
        pass
    
    def get_framework_info(self) -> Dict[str, Any]:
        """获取框架信息"""
        return {
            "name": self.FRAMEWORK_NAME,
            "version": "1.0.0"
        }
```

### AgentResponse

Agent响应封装类。

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class AgentResponse:
    """Agent响应封装"""
    
    content: str = ""                           # 响应内容
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)  # 工具调用
    metadata: Dict[str, Any] = field(default_factory=dict)          # 元数据
```

---

## 自定义适配器

### 实现步骤

1. 继承BaseAdapter
2. 设置FRAMEWORK_NAME
3. 实现run_single_turn方法
4. 实现run_multi_turn方法
5. (可选)实现get_framework_info方法

### 示例：为自定义框架创建适配器

```python
from agenteval.adapters import BaseAdapter, AgentResponse
from agenteval.models import AgentConfig

class MyFrameworkAdapter(BaseAdapter):
    """自定义框架适配器"""
    
    FRAMEWORK_NAME = "my_framework"
    
    def _validate_config(self):
        """验证配置"""
        if self.agent_config.agent_instance is None:
            raise ValueError("Agent instance is required")
    
    async def run_single_turn(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Any]] = None
    ) -> AgentResponse:
        """执行单轮对话"""
        agent = self.agent_config.agent_instance
        
        try:
            # 调用你的Agent
            result = await agent.arun(message)
            
            # 提取工具调用信息（如果有）
            tool_calls = self._extract_tool_calls(result)
            
            return AgentResponse(
                content=result.text,
                tool_calls=tool_calls,
                metadata={
                    "framework": self.FRAMEWORK_NAME,
                    "latency_ms": result.latency
                }
            )
        except Exception as e:
            return AgentResponse(
                content="",
                metadata={"error": str(e)}
            )
    
    async def run_multi_turn(
        self,
        messages: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Any]] = None
    ) -> AgentResponse:
        """执行多轮对话"""
        # 获取最后一条用户消息
        last_message = messages[-1]["content"] if messages else ""
        
        # 简化实现：单轮处理
        return await self.run_single_turn(last_message, context, tools)
    
    def _extract_tool_calls(self, result) -> List[Dict[str, Any]]:
        """提取工具调用信息"""
        tool_calls = []
        
        if hasattr(result, 'tool_calls'):
            for call in result.tool_calls:
                tool_calls.append({
                    "name": call.name,
                    "input": call.arguments,
                    "output": call.result
                })
        
        return tool_calls
    
    def get_framework_info(self) -> Dict[str, Any]:
        """获取框架信息"""
        return {
            "name": "My Framework",
            "version": "1.0.0",
            "supported_features": ["single_turn", "multi_turn", "tool_use"]
        }
```

### 使用自定义适配器

```python
from agenteval import EvaluationEngine
from agenteval.models import AgentConfig

# 创建自定义Agent
my_agent = MyCustomAgent()

# 配置适配器
config = AgentConfig(
    framework="my_framework",
    agent_instance=my_agent
)
adapter = MyFrameworkAdapter(config)

# 使用
engine = EvaluationEngine()
engine.set_adapter(adapter)
result = await engine.evaluate_single(test_case)
```

---

## 插件注册

### 使用装饰器注册

```python
from agenteval.plugins import register_adapter
from agenteval.adapters import BaseAdapter

@register_adapter("my_framework")
class MyFrameworkAdapter(BaseAdapter):
    FRAMEWORK_NAME = "my_framework"
    ...
```

### 手动注册

```python
from agenteval.plugins import get_registry

registry = get_registry()
registry.register_adapter("my_framework", MyFrameworkAdapter)
```

### 自动发现

AgentEval支持从指定包自动发现插件：

```python
from agenteval.plugins import get_registry

registry = get_registry()
registry.discover_plugins("my_plugins_package")
```

---

## 最佳实践

### 1. 错误处理

```python
async def run_single_turn(self, message, context=None, tools=None):
    try:
        result = await self.agent.arun(message)
        return AgentResponse(content=result)
    except TimeoutError:
        return AgentResponse(
            content="",
            metadata={"error": "timeout"}
        )
    except Exception as e:
        return AgentResponse(
            content="",
            metadata={"error": str(e)}
        )
```

### 2. 工具调用提取

```python
def _extract_tool_calls(self, result) -> List[Dict[str, Any]]:
    """统一的工具调用提取方法"""
    tool_calls = []
    
    # 处理不同格式的工具调用
    if hasattr(result, 'tool_calls'):
        for call in result.tool_calls:
            tool_calls.append({
                "name": getattr(call, 'name', 'unknown'),
                "input": getattr(call, 'arguments', {}),
                "output": getattr(call, 'result', None)
            })
    
    return tool_calls
```

### 3. 性能监控

```python
import time

async def run_single_turn(self, message, context=None, tools=None):
    start_time = time.time()
    
    result = await self.agent.arun(message)
    
    latency_ms = (time.time() - start_time) * 1000
    
    return AgentResponse(
        content=result,
        metadata={"latency_ms": latency_ms}
    )
```

### 4. 流式响应支持

```python
from typing import AsyncIterator

async def run_streaming(
    self,
    message: str,
    context: Optional[Dict[str, Any]] = None
) -> AsyncIterator[str]:
    """流式响应（可选实现）"""
    async for chunk in self.agent.astream(message):
        yield chunk
```

---

## 常见问题

### Q: 如何选择适配器？

A: 根据你的Agent框架选择：
- LangChain → LangChainAdapter
- CrewAI → CrewAIAdapter
- AutoGen → AutoGenAdapter
- 自定义Agent → CallableAdapter 或 自定义适配器

### Q: 适配器支持同步Agent吗？

A: 是的。对于同步Agent，可以在适配器中使用asyncio.to_thread包装：

```python
import asyncio

async def run_single_turn(self, message, context=None, tools=None):
    # 包装同步调用
    result = await asyncio.to_thread(self.agent.run, message)
    return AgentResponse(content=result)
```

### Q: 如何处理Agent的状态管理？

A: 可以在适配器中维护状态：

```python
class StatefulAdapter(BaseAdapter):
    def __init__(self, agent_config):
        super().__init__(agent_config)
        self.conversation_history = []
    
    async def run_single_turn(self, message, context=None, tools=None):
        # 添加到历史
        self.conversation_history.append({"role": "user", "content": message})
        
        # 调用Agent
        result = await self.agent.arun(self.conversation_history)
        
        # 添加响应到历史
        self.conversation_history.append({"role": "assistant", "content": result})
        
        return AgentResponse(content=result)
```

---

**文档版本**: v1.0.0
**最后更新**: 2026-03-25
