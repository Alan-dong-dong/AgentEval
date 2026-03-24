"""
任务和测试用例数据模型
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
import uuid


class TaskType(Enum):
    """任务类型枚举"""

    SINGLE_TURN = "single_turn"
    MULTI_TURN = "multi_turn"
    TOOL_USE = "tool_use"
    PLANNING = "planning"
    CODE_GEN = "code_gen"
    CUSTOM = "custom"


class TaskDifficulty(Enum):
    """任务难度"""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


@dataclass
class ToolDefinition:
    """工具定义

    Attributes:
        name: 工具名称
        description: 工具描述
        parameters: 工具参数定义
        mock_response: 可选的模拟响应
    """

    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    mock_response: Optional[Any] = None


@dataclass
class TestCase:
    """测试用例

    定义一个完整的测试场景，包括输入、期望输出和评估标准。

    Attributes:
        id: 唯一标识符
        name: 测试用例名称
        description: 测试用例描述
        task_type: 任务类型
        difficulty: 任务难度
        input_message: 输入消息
        context: 额外上下文信息
        tools: 可用工具列表
        conversation_history: 多轮对话历史
        expected_output: 期望输出
        expected_tool_calls: 期望的工具调用列表
        evaluation_criteria: 评估标准
        tags: 标签列表
        metadata: 元数据

    Example:
        >>> test_case = TestCase(
        ...     name="simple_qa",
        ...     input_message="What is 2+2?",
        ...     expected_output="4"
        ... )
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    task_type: TaskType = TaskType.SINGLE_TURN
    difficulty: TaskDifficulty = TaskDifficulty.MEDIUM
    input_message: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    tools: List[ToolDefinition] = field(default_factory=list)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    expected_output: Optional[str] = None
    expected_tool_calls: List[str] = field(default_factory=list)
    evaluation_criteria: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type.value,
            "difficulty": self.difficulty.value,
            "input_message": self.input_message,
            "context": self.context,
            "tools": [
                {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                }
                for t in self.tools
            ],
            "conversation_history": self.conversation_history,
            "expected_output": self.expected_output,
            "expected_tool_calls": self.expected_tool_calls,
            "evaluation_criteria": self.evaluation_criteria,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestCase":
        """从字典创建TestCase"""
        tools = []
        for t in data.get("tools", []):
            tools.append(
                ToolDefinition(
                    name=t["name"],
                    description=t.get("description", ""),
                    parameters=t.get("parameters", {}),
                )
            )

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            task_type=TaskType(data.get("task_type", "single_turn")),
            difficulty=TaskDifficulty(data.get("difficulty", "medium")),
            input_message=data.get("input_message", ""),
            context=data.get("context", {}),
            tools=tools,
            conversation_history=data.get("conversation_history", []),
            expected_output=data.get("expected_output"),
            expected_tool_calls=data.get("expected_tool_calls", []),
            evaluation_criteria=data.get("evaluation_criteria", {}),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )


@dataclass
class AgentConfig:
    """Agent配置

    Attributes:
        framework: 框架名称 (langchain, crewai, autogen, callable)
        agent_instance: Agent实例
        agent_callable: 可调用Agent函数
        config: 额外配置
    """

    framework: str = "callable"
    agent_instance: Optional[Any] = None
    agent_callable: Optional[Callable] = None
    config: Dict[str, Any] = field(default_factory=dict)
