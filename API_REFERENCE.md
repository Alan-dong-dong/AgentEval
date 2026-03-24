# AgentEval API 参考文档

## 目录

- [快速评估 API](#快速评估-api)
- [评估引擎 API](#评估引擎-api)
- [评估器 API](#评估器-api)
- [适配器 API](#适配器-api)
- [数据模型](#数据模型)
- [预设数据集](#预设数据集)
- [CLI 命令](#cli-命令)

---

## 快速评估 API

### quick_eval()

最简单的评估接口，一行代码完成评估。

```python
from agenteval import quick_eval

result = quick_eval(
    agent: Union[Callable, Any],
    prompt: str,
    expected: str = None
) -> Dict[str, Any]
```

**参数说明：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| agent | Callable 或 Agent实例 | 是 | 要评估的Agent |
| prompt | str | 是 | 测试提示词 |
| expected | str | 否 | 期望输出 |

**返回值：**

```python
{
    "success": bool,          # 是否成功执行
    "score": float,           # 综合分数 0-1
    "response": str,          # Agent响应内容
    "latency_ms": float,      # 响应延迟(毫秒)
    "details": {              # 详细评估结果
        "correctness": {"score": 0.95, "details": "..."},
        "efficiency": {"score": 0.88, "details": "..."}
    }
}
```

**示例：**

```python
from agenteval import quick_eval

# 评估简单函数
def my_agent(prompt: str) -> str:
    return "The answer is 42"

result = quick_eval(my_agent, "What is the meaning of life?")
print(f"Score: {result['score']:.2f}")

# 评估带期望输出
result = quick_eval(my_agent, "What is 2+2?", expected="4")
print(f"Score: {result['score']:.2f}")
print(f"Response: {result['response']}")
```

---

## 评估引擎 API

### EvaluationEngine

核心评估引擎，提供完整的评估能力。

```python
from agenteval import EvaluationEngine

engine = EvaluationEngine(config: Dict[str, Any] = None)
```

**配置选项：**

```python
config = {
    "max_concurrency": 5,     # 最大并发数 (默认: 5)
    "timeout": 30,            # 单次评估超时秒数 (默认: 30)
    "retry_count": 3,         # 失败重试次数 (默认: 3)
    "log_level": "INFO",      # 日志级别 (默认: "INFO")
    "cache_enabled": False,   # 是否启用缓存 (默认: False)
    "cache_ttl": 3600         # 缓存过期时间秒数 (默认: 3600)
}
```

#### set_adapter()

设置框架适配器。

```python
def set_adapter(self, adapter: BaseAdapter) -> None
```

**参数：**
- adapter (BaseAdapter): 框架适配器实例

**示例：**

```python
from agenteval.adapters import LangChainAdapter
from agenteval.models import AgentConfig

config = AgentConfig(
    framework="langchain",
    agent_instance=my_langchain_agent
)
adapter = LangChainAdapter(config)
engine.set_adapter(adapter)
```

#### add_evaluator()

添加单个评估器。

```python
def add_evaluator(self, evaluator: BaseEvaluator) -> None
```

**参数：**
- evaluator (BaseEvaluator): 评估器实例

**示例：**

```python
from agenteval.evaluators import CorrectnessEvaluator

engine.add_evaluator(CorrectnessEvaluator(model="gpt-4"))
```

#### add_evaluators()

批量添加评估器。

```python
def add_evaluators(self, evaluators: List[BaseEvaluator]) -> None
```

**参数：**
- evaluators (List[BaseEvaluator]): 评估器列表

**示例：**

```python
from agenteval.evaluators import CorrectnessEvaluator, ToolUsageEvaluator, EfficiencyEvaluator

engine.add_evaluators([
    CorrectnessEvaluator(weight=1.0),
    ToolUsageEvaluator(weight=0.8),
    EfficiencyEvaluator(weight=0.5)
])
```

#### evaluate_single()

执行单个测试用例评估。

```python
async def evaluate_single(
    self,
    test_case: TestCase,
    context: Dict[str, Any] = None
) -> EvaluationResult
```

**参数：**
- test_case (TestCase): 测试用例
- context (Dict[str, Any], 可选): 额外上下文信息

**返回值：**
- EvaluationResult: 评估结果对象

**示例：**

```python
from agenteval.models import TestCase

test_case = TestCase(
    name="simple_qa",
    input_message="What is the capital of France?",
    expected_output="Paris"
)

result = await engine.evaluate_single(test_case)
print(f"Score: {result.overall_score:.2f}")
print(f"Latency: {result.latency_ms:.2f}ms")
```

#### evaluate_batch()

批量执行评估。

```python
async def evaluate_batch(
    self,
    test_cases: List[TestCase],
    context: Dict[str, Any] = None
) -> BenchmarkResult
```

**参数：**
- test_cases (List[TestCase]): 测试用例列表
- context (Dict[str, Any], 可选): 额外上下文信息

**返回值：**
- BenchmarkResult: 基准测试结果对象

**示例：**

```python
test_cases = [
    TestCase(name="qa1", input_message="What is 2+2?", expected_output="4"),
    TestCase(name="qa2", input_message="What is 3+3?", expected_output="6"),
    TestCase(name="qa3", input_message="What is 4*4?", expected_output="16")
]

result = await engine.evaluate_batch(test_cases)
print(f"Passed: {result.passed_tests}/{result.total_tests}")
print(f"Average Score: {result.average_score:.2f}")
print(f"Duration: {result.duration_seconds:.2f}s")
```

#### get_results()

获取所有评估结果。

```python
def get_results(self) -> List[EvaluationResult]
```

#### clear_results()

清空评估结果。

```python
def clear_results(self) -> None
```

---

## 评估器 API

### BaseEvaluator

评估器基类，所有自定义评估器需继承此类。

```python
from agenteval.evaluators import BaseEvaluator, MetricScore

class MyEvaluator(BaseEvaluator):
    """自定义评估器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name = "MyCustomEvaluator"
    
    async def evaluate(
        self,
        test_case: TestCase,
        agent_response: str,
        context: Dict[str, Any] = None
    ) -> MetricScore:
        # 实现评估逻辑
        score = self._calculate_score(agent_response)
        
        return MetricScore(
            name=self.name,
            score=score,
            weight=1.0,
            details="Evaluation completed"
        )
    
    def _calculate_score(self, response: str) -> float:
        # 自定义评分逻辑
        return 0.95
```

### 内置评估器

#### CorrectnessEvaluator

评估Agent输出的功能正确性。

```python
from agenteval.evaluators import CorrectnessEvaluator

evaluator = CorrectnessEvaluator(
    model="gpt-4",              # 用于评估的LLM模型 (默认: "gpt-4")
    threshold=0.7,              # 通过阈值 (默认: 0.7)
    weight=1.0,                 # 权重 (默认: 1.0)
    strict_mode=False           # 严格模式 (默认: False)
)
```

**评估维度：**
- 任务理解准确性
- 输出完整性
- 信息准确性
- 逻辑一致性

**示例：**

```python
from agenteval.evaluators import CorrectnessEvaluator

evaluator = CorrectnessEvaluator(model="gpt-4", threshold=0.8)
score = await evaluator.evaluate(test_case, agent_response, context)
print(f"Correctness Score: {score.score:.2f}")
```

#### ToolUsageEvaluator

评估工具使用准确性。

```python
from agenteval.evaluators import ToolUsageEvaluator

evaluator = ToolUsageEvaluator(
    strict_mode=False,          # 严格模式 (默认: False)
    weight=0.8,                 # 权重 (默认: 0.8)
    allow_extra_tools=False     # 允许额外工具 (默认: False)
)
```

**评估维度：**
- 工具选择正确性
- 参数正确性
- 调用顺序
- 调用效率

**示例：**

```python
from agenteval.evaluators import ToolUsageEvaluator

evaluator = ToolUsageEvaluator(strict_mode=True)
score = await evaluator.evaluate(test_case, agent_response, context)
print(f"Tool Usage Score: {score.score:.2f}")
print(f"Precision: {score.metadata['precision']:.2f}")
print(f"Recall: {score.metadata['recall']:.2f}")
```

#### EfficiencyEvaluator

评估响应效率。

```python
from agenteval.evaluators import EfficiencyEvaluator

evaluator = EfficiencyEvaluator(
    latency_threshold_ms=5000,  # 延迟阈值毫秒 (默认: 5000)
    token_threshold=1000,       # Token阈值 (默认: 1000)
    weight=0.5                  # 权重 (默认: 0.5)
)
```

**评估维度：**
- 响应延迟
- Token消耗
- 成本效率

**示例：**

```python
from agenteval.evaluators import EfficiencyEvaluator

evaluator = EfficiencyEvaluator(latency_threshold_ms=3000)
score = await evaluator.evaluate(test_case, agent_response, context)
print(f"Efficiency Score: {score.score:.2f}")
print(f"Latency: {score.metadata['latency_ms']:.2f}ms")
```

#### SafetyEvaluator

评估安全合规性。

```python
from agenteval.evaluators import SafetyEvaluator

evaluator = SafetyEvaluator(
    categories=["harmful", "bias", "privacy"],  # 评估类别
    weight=1.0                                   # 权重 (默认: 1.0)
)
```

**评估维度：**
- 有害内容检测
- 偏见检测
- 隐私保护
- 政策合规

**示例：**

```python
from agenteval.evaluators import SafetyEvaluator

evaluator = SafetyEvaluator(categories=["harmful", "bias"])
score = await evaluator.evaluate(test_case, agent_response, context)
print(f"Safety Score: {score.score:.2f}")
```

#### ConversationEvaluator

评估对话质量。

```python
from agenteval.evaluators import ConversationEvaluator

evaluator = ConversationEvaluator(
    model="gpt-4",              # 用于评估的LLM模型
    weight=0.8                  # 权重 (默认: 0.8)
)
```

**评估维度：**
- 上下文保持
- 多轮连贯性
- 意图理解
- 响应相关性

**示例：**

```python
from agenteval.evaluators import ConversationEvaluator

evaluator = ConversationEvaluator(model="gpt-4")
score = await evaluator.evaluate(test_case, agent_response, context)
print(f"Conversation Score: {score.score:.2f}")
```

---

## 适配器 API

### BaseAdapter

适配器基类。

```python
from agenteval.adapters import BaseAdapter, AgentResponse

class MyAdapter(BaseAdapter):
    """自定义适配器"""
    
    FRAMEWORK_NAME = "my_framework"
    
    async def run_single_turn(
        self,
        message: str,
        context: Dict[str, Any] = None,
        tools: List[Any] = None
    ) -> AgentResponse:
        # 调用你的Agent
        response = await my_agent.arun(message)
        
        return AgentResponse(
            content=response.text,
            tool_calls=response.tool_calls,
            metadata={"framework": self.FRAMEWORK_NAME}
        )
    
    async def run_multi_turn(
        self,
        messages: List[Dict[str, str]],
        context: Dict[str, Any] = None,
        tools: List[Any] = None
    ) -> AgentResponse:
        # 实现多轮对话逻辑
        last_message = messages[-1]["content"]
        return await self.run_single_turn(last_message, context, tools)
    
    def get_framework_info(self) -> Dict[str, Any]:
        return {
            "name": "My Framework",
            "version": "1.0.0",
            "supported_features": ["single_turn", "multi_turn"]
        }
```

### AgentResponse

Agent响应封装。

```python
@dataclass
class AgentResponse:
    content: str                          # 响应内容
    tool_calls: List[Dict[str, Any]]      # 工具调用记录
    metadata: Dict[str, Any]              # 元数据
```

**属性说明：**

| 属性 | 类型 | 说明 |
|------|------|------|
| content | str | Agent的响应文本 |
| tool_calls | List[Dict] | 工具调用记录列表 |
| metadata | Dict | 额外元数据 |

### LangChainAdapter

LangChain框架适配器。

```python
from agenteval.adapters import LangChainAdapter
from agenteval.models import AgentConfig

config = AgentConfig(
    framework="langchain",
    agent_instance=my_langchain_agent
)
adapter = LangChainAdapter(config)
```

### CrewAIAdapter

CrewAI框架适配器。

```python
from agenteval.adapters import CrewAIAdapter
from agenteval.models import AgentConfig

config = AgentConfig(
    framework="crewai",
    agent_instance=my_crew
)
adapter = CrewAIAdapter(config)
```

### AutoGenAdapter

AutoGen框架适配器。

```python
from agenteval.adapters import AutoGenAdapter
from agenteval.models import AgentConfig

config = AgentConfig(
    framework="autogen",
    agent_instance=my_autogen_agent
)
adapter = AutoGenAdapter(config)
```

---

## 数据模型

### TestCase

测试用例定义。

```python
from agenteval.models import TestCase, TaskType, TaskDifficulty

test_case = TestCase(
    id="test_001",                          # 唯一标识
    name="simple_qa",                       # 名称
    description="Simple QA test",           # 描述
    task_type=TaskType.SINGLE_TURN,         # 任务类型
    difficulty=TaskDifficulty.EASY,         # 难度
    input_message="What is 2+2?",          # 输入消息
    expected_output="4",                    # 期望输出
    tools=[],                               # 工具定义
    conversation_history=[],                # 对话历史
    evaluation_criteria={},                 # 评估标准
    tags=["math", "simple"],               # 标签
    metadata={}                             # 元数据
)
```

**TaskType枚举：**
- SINGLE_TURN: 单轮对话
- MULTI_TURN: 多轮对话
- TOOL_USE: 工具调用
- PLANNING: 规划任务
- CODE_GEN: 代码生成
- CUSTOM: 自定义

**TaskDifficulty枚举：**
- EASY: 简单
- MEDIUM: 中等
- HARD: 困难
- EXPERT: 专家级

### ToolDefinition

工具定义。

```python
from agenteval.models import ToolDefinition

tool = ToolDefinition(
    name="calculator",
    description="Perform mathematical calculations",
    parameters={
        "expression": {
            "type": "string",
            "description": "Mathematical expression to evaluate"
        }
    },
    mock_response=None  # 可选的模拟响应
)
```

### MetricScore

评估分数。

```python
from agenteval.models import MetricScore

score = MetricScore(
    name="correctness",      # 评估器名称
    score=0.95,              # 分数 0-1
    weight=1.0,              # 权重
    details="...",           # 详细说明
    metadata={}              # 元数据
)
```

### EvaluationResult

单次评估结果。

```python
from agenteval.models import EvaluationResult

result = EvaluationResult(
    test_case_id="test_001",           # 测试用例ID
    agent_response="The answer is 4",  # Agent响应
    tool_calls=[],                     # 工具调用
    scores=[score1, score2],           # 评分明细
    overall_score=0.92,                # 综合分数
    latency_ms=245.5,                  # 延迟
    token_usage={"total": 350},        # Token使用
    success=True,                      # 是否成功
    error_message="",                  # 错误信息
    timestamp=datetime.now()           # 时间戳
)
```

### BenchmarkResult

基准测试结果。

```python
from agenteval.models import BenchmarkResult

benchmark = BenchmarkResult(
    id="benchmark_001",                # 基准测试ID
    name="QA Benchmark",              # 名称
    results=[result1, result2],        # 所有结果
    total_tests=50,                    # 总测试数
    passed_tests=45,                   # 通过数
    failed_tests=5,                    # 失败数
    average_score=0.89,                # 平均分数
    dimension_scores={                 # 各维度分数
        "correctness": 0.92,
        "efficiency": 0.85
    },
    duration_seconds=12.5,             # 总耗时
    start_time=datetime.now(),         # 开始时间
    end_time=datetime.now()            # 结束时间
)
```

---

## 预设数据集

### PresetDatasets

预设数据集类，提供开箱即用的测试数据。

```python
from agenteval.simple.presets import PresetDatasets
```

#### get_basic_qa()

获取基础问答测试集。

```python
test_cases = PresetDatasets.get_basic_qa() -> List[TestCase]
```

**包含测试：**
- 简单数学计算
- 事实性知识
- 逻辑推理

#### get_tool_use_tests()

获取工具使用测试集。

```python
test_cases = PresetDatasets.get_tool_use_tests() -> List[TestCase]
```

**包含测试：**
- 计算器工具
- 搜索工具
- API调用

#### get_safety_tests()

获取安全测试集。

```python
test_cases = PresetDatasets.get_safety_tests() -> List[TestCase]
```

**包含测试：**
- 有害请求拒绝
- 偏见响应检测
- 隐私保护

#### get_conversation_tests()

获取对话测试集。

```python
test_cases = PresetDatasets.get_conversation_tests() -> List[TestCase]
```

**包含测试：**
- 上下文保持
- 多轮连贯性
- 意图理解

#### get_all_presets()

获取所有预设数据集。

```python
all_presets = PresetDatasets.get_all_presets() -> Dict[str, List[TestCase]]
```

**返回：**
```python
{
    "basic_qa": [...],
    "tool_use": [...],
    "safety": [...],
    "conversation": [...]
}
```

---

## CLI 命令

### agenteval quick

快速评估Agent。

```bash
agenteval quick <agent_module> <prompt> [OPTIONS]
```

**参数：**
- agent_module: Agent模块路径，如 `mymodule.my_agent`
- prompt: 测试提示词

**选项：**
- --expected: 期望输出
- --framework: 框架类型 (默认: "callable")
- --model: 评估模型 (默认: "gpt-4")
- --timeout: 超时秒数 (默认: 30)

**示例：**

```bash
# 基础评估
agenteval quick mymodule.my_agent "What is 2+2?"

# 带期望输出
agenteval quick mymodule.my_agent "What is 2+2?" --expected "4"

# 指定框架
agenteval quick mymodule.my_agent "What is 2+2?" --framework langchain
```

### agenteval run

运行评估套件。

```bash
agenteval run <config_file> [OPTIONS]
```

**参数：**
- config_file: 配置文件路径 (YAML或JSON)

**选项：**
- --output, -o: 结果输出路径
- --format: 输出格式 (json/csv/html)
- --verbose, -v: 详细输出

**示例：**

```bash
# 运行评估
agenteval run eval_config.yaml

# 输出结果到文件
agenteval run eval_config.yaml --output results.json

# 生成HTML报告
agenteval run eval_config.yaml --format html --output report.html
```

**配置文件示例：**

```yaml
# eval_config.yaml
agent:
  module: mymodule.my_agent
  framework: callable

dataset:
  type: preset
  name: basic_qa
  # 或自定义数据集
  # type: custom
  # path: ./test_cases.json

evaluators:
  - name: correctness
    model: gpt-4
    threshold: 0.8
  - name: efficiency
    latency_threshold_ms: 3000

settings:
  max_concurrency: 5
  timeout: 30
  retry_count: 3
```

### agenteval preset

使用预设数据集评估。

```bash
agenteval preset <agent_module> [OPTIONS]
```

**参数：**
- agent_module: Agent模块路径

**选项：**
- --dataset: 数据集名称 (basic_qa/tool_use/safety/conversation)
- --output, -o: 结果输出路径
- --format: 输出格式

**示例：**

```bash
# 使用基础问答数据集
agenteval preset mymodule.my_agent --dataset basic_qa

# 使用工具使用数据集
agenteval preset mymodule.my_agent --dataset tool_use

# 输出结果
agenteval preset mymodule.my_agent --dataset safety --output results.json
```

### agenteval report

生成评估报告。

```bash
agenteval report <result_file> [OPTIONS]
```

**参数：**
- result_file: 评估结果文件路径

**选项：**
- --format: 报告格式 (html/json/csv)
- --output, -o: 报告输出路径
- --template: 报告模板路径

**示例：**

```bash
# 生成HTML报告
agenteval report results.json --format html --output report.html

# 使用自定义模板
agenteval report results.json --template my_template.html --output report.html
```

### agenteval list

列出可用的评估器和数据集。

```bash
agenteval list [OPTIONS]
```

**选项：**
- --type: 列出类型 (evaluators/datasets/adapters/all)

**示例：**

```bash
# 列出所有评估器
agenteval list --type evaluators

# 列出所有数据集
agenteval list --type datasets

# 列出所有
agenteval list --type all
```

---

## 错误处理

### 异常类型

AgentEval定义了以下异常类型：

```python
from agenteval.exceptions import (
    AgentEvalError,           # 基础异常
    AdapterError,             # 适配器错误
    EvaluatorError,           # 评估器错误
    TimeoutError,             # 超时错误
    ConfigurationError,       # 配置错误
    DatasetError,             # 数据集错误
    ValidationError           # 验证错误
)
```

### 错误处理示例

```python
from agenteval import EvaluationEngine
from agenteval.exceptions import AdapterError, TimeoutError

engine = EvaluationEngine()

try:
    result = await engine.evaluate_single(test_case)
except AdapterError as e:
    print(f"适配器错误: {e}")
except TimeoutError as e:
    print(f"评估超时: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

---

## 配置参考

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| AGENTEVAL_LOG_LEVEL | 日志级别 | INFO |
| AGENTEVAL_MAX_CONCURRENCY | 最大并发数 | 5 |
| AGENTEVAL_TIMEOUT | 超时秒数 | 30 |
| OPENAI_API_KEY | OpenAI API密钥 | - |
| ANTHROPIC_API_KEY | Anthropic API密钥 | - |

### 配置文件

支持YAML和JSON格式的配置文件。

```yaml
# agenteval.yaml
engine:
  max_concurrency: 5
  timeout: 30
  retry_count: 3

evaluators:
  correctness:
    model: gpt-4
    threshold: 0.8
  efficiency:
    latency_threshold_ms: 3000

storage:
  type: json
  path: ./results

logging:
  level: INFO
  file: agenteval.log
```

---

**文档版本**: v1.0.0
**最后更新**: 2026-03-25
