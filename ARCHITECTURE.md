# AgentEval 架构设计文档

## 目录

- [系统概览](#系统概览)
- [架构图](#架构图)
- [核心模块](#核心模块)
- [数据流设计](#数据流设计)
- [扩展机制](#扩展机制)
- [设计决策](#设计决策)
- [性能考量](#性能考量)
- [安全设计](#安全设计)

---

## 系统概览

AgentEval采用分层架构设计，确保系统的可扩展性、可维护性和高性能。每一层都有明确的职责，通过标准化接口进行通信。

### 设计原则

1. **关注点分离**：每层专注单一职责
2. **可扩展性**：支持插件和自定义扩展
3. **框架无关**：统一接口屏蔽框架差异
4. **简单易用**：提供简单和高级两种使用模式

---

## 架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           用户接口层 (User Interface)                        │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐           │
│  │   简单模式 (Simple Mode)     │  │   高级模式 (Advanced Mode)   │           │
│  │  - CLI 命令                 │  │  - Python API               │           │
│  │  - YAML 配置文件            │  │  - 自定义评估器              │           │
│  │  - 预设评估模板             │  │  - 批量评估管道              │           │
│  └─────────────────────────────┘  └─────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           核心引擎层 (Core Engine)                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │   评估调度器      │  │   任务管理器      │  │   结果聚合器      │          │
│  │   (Evaluator)    │  │   (TaskManager)  │  │   (Aggregator)   │          │
│  │  - 编排评估流程   │  │  - 管理测试用例   │  │  - 收集评估结果   │          │
│  │  - 并发控制       │  │  - 数据集管理     │  │  - 统计分析       │          │
│  │  - 超时处理       │  │  - 预设模板       │  │  - 生成报告       │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           评估器层 (Evaluators)                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │
│  │  功能正确性   │ │  响应效率    │ │  安全合规    │ │  工具使用    │      │
│  │  Evaluator   │ │  Evaluator   │ │  Evaluator   │ │  Evaluator   │      │
│  │              │ │              │ │              │ │              │      │
│  │ - 任务理解    │ │ - 延迟评估   │ │ - 有害内容   │ │ - 工具选择   │      │
│  │ - 输出完整性  │ │ - Token效率  │ │ - 偏见检测   │ │ - 参数正确   │      │
│  │ - 逻辑一致性  │ │ - 成本评估   │ │ - 隐私保护   │ │ - 调用顺序   │      │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                        │
│  │  对话质量    │ │  规划质量    │ │  自定义      │                        │
│  │  Evaluator   │ │  Evaluator   │ │  Evaluator   │                        │
│  │              │ │              │ │              │                        │
│  │ - 上下文保持  │ │ - 计划合理性 │ │ - 用户定义   │                        │
│  │ - 多轮连贯性  │ │ - 步骤完整性 │ │ - 规则扩展   │                        │
│  │ - 意图理解    │ │ - 执行效率   │ │ - LLM评估    │                        │
│  └──────────────┘ └──────────────┘ └──────────────┘                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           适配器层 (Adapters)                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │
│  │  LangChain   │ │   CrewAI     │ │   AutoGen    │ │   Custom     │      │
│  │  Adapter     │ │   Adapter    │ │   Adapter    │ │   Adapter    │      │
│  │              │ │              │ │              │ │              │      │
│  │ - Agent类型   │ │ - Crew编排   │ │ - 多Agent    │ │ - Callable   │      │
│  │ - 链式调用    │ │ - 角色定义   │ │ - 对话管理   │ │ - 自定义接口  │      │
│  │ - 工具集成    │ │ - 任务分配   │ │ - 群组协作   │ │ - 灵活扩展   │      │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           数据层 (Data Layer)                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │   测试数据集      │  │   结果存储       │  │   配置管理       │          │
│  │   (Datasets)     │  │   (Storage)      │  │   (Config)       │          │
│  │  - 预设数据集     │  │  - JSON存储      │  │  - YAML配置      │          │
│  │  - 自定义数据     │  │  - 数据库支持     │  │  - 环境变量      │          │
│  │  - 数据加载       │  │  - 导出功能       │  │  - 默认配置      │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 核心模块

### 1. 目录结构

```
agenteval/
├── __init__.py                    # 包初始化
├── cli/                           # 命令行接口
│   ├── __init__.py
│   ├── commands.py                # CLI命令定义
│   └── simple_commands.py         # 简单命令
├── core/                          # 核心引擎
│   ├── __init__.py
│   ├── engine.py                  # 评估引擎
│   ├── task.py                    # 任务定义
│   ├── runner.py                  # 任务执行器
│   └── aggregator.py              # 结果聚合
├── evaluators/                    # 评估器
│   ├── __init__.py
│   ├── base.py                    # 基础评估器
│   ├── correctness.py             # 功能正确性
│   ├── efficiency.py              # 响应效率
│   ├── safety.py                  # 安全合规
│   ├── conversation.py            # 对话质量
│   ├── tool_usage.py              # 工具使用
│   └── custom.py                  # 自定义评估器
├── adapters/                      # 框架适配器
│   ├── __init__.py
│   ├── base.py                    # 基础适配器
│   ├── langchain.py               # LangChain适配器
│   ├── autogen.py                 # AutoGen适配器
│   ├── crewai.py                  # CrewAI适配器
│   └── llamaindex.py              # LlamaIndex适配器
├── data/                          # 数据管理
│   ├── __init__.py
│   ├── dataset.py                 # 数据集管理
│   ├── testcase.py                # 测试用例
│   └── storage.py                 # 存储接口
├── models/                        # 数据模型
│   ├── __init__.py
│   ├── task.py                    # 任务模型
│   ├── result.py                  # 结果模型
│   └── config.py                  # 配置模型
├── simple/                        # 简单模式
│   ├── __init__.py
│   ├── presets.py                 # 预设模板
│   └── quick_eval.py              # 快速评估
├── plugins/                       # 插件系统
│   ├── __init__.py
│   └── registry.py                # 插件注册
└── utils/                         # 工具函数
    ├── __init__.py
    ├── logger.py                  # 日志工具
    └── helpers.py                 # 辅助函数
```

### 2. 核心引擎 (Core Engine)

#### EvaluationEngine

评估引擎是系统的核心，负责编排整个评估流程。

**主要职责：**
- 管理评估器和适配器
- 编排评估流程
- 控制并发执行
- 聚合评估结果

**关键方法：**
```python
class EvaluationEngine:
    def set_adapter(self, adapter: BaseAdapter)  # 设置适配器
    def add_evaluator(self, evaluator: BaseEvaluator)  # 添加评估器
    async def evaluate_single(self, test_case)  # 单个评估
    async def evaluate_batch(self, test_cases)  # 批量评估
```

#### TaskManager

任务管理器负责管理测试用例和数据集。

**主要职责：**
- 加载和管理测试用例
- 提供预设数据集
- 支持数据集导入导出

#### Aggregator

结果聚合器负责收集和分析评估结果。

**主要职责：**
- 收集单个评估结果
- 计算统计指标
- 生成评估报告

### 3. 评估器 (Evaluators)

#### 三层评估架构

**推理层 (Reasoning Layer)**
- PlanQualityMetric: 评估计划质量
- PlanAdherenceMetric: 评估计划遵循度

**行动层 (Action Layer)**
- ToolCorrectnessMetric: 评估工具选择正确性
- ArgumentCorrectnessMetric: 评估参数正确性

**执行层 (Execution Layer)**
- TaskCompletionMetric: 评估任务完成度
- StepEfficiencyMetric: 评估执行效率

#### 评估器类型

1. **RuleBasedEvaluator** - 基于规则的评估
2. **LLMBasedEvaluator** - 基于LLM的评估
3. **CustomEvaluator** - 自定义评估

### 4. 适配器 (Adapters)

#### 设计原则

- **统一接口**：所有适配器实现相同接口
- **框架无关**：屏蔽底层框架差异
- **可扩展**：支持自定义适配器

#### 适配器接口

```python
class BaseAdapter(ABC):
    FRAMEWORK_NAME: str
    
    async def run_single_turn(self, message, context, tools) -> AgentResponse
    async def run_multi_turn(self, messages, context, tools) -> AgentResponse
    def get_framework_info(self) -> Dict
```

### 5. 数据模型 (Data Models)

#### TestCase

测试用例数据模型，定义评估输入和期望输出。

```python
@dataclass
class TestCase:
    id: str                          # 唯一标识
    name: str                        # 名称
    input_message: str               # 输入消息
    expected_output: Optional[str]   # 期望输出
    tools: List[ToolDefinition]      # 工具定义
    conversation_history: List[Dict] # 对话历史
    evaluation_criteria: Dict        # 评估标准
    tags: List[str]                  # 标签
```

#### EvaluationResult

单次评估结果数据模型。

```python
@dataclass
class EvaluationResult:
    test_case_id: str                # 测试用例ID
    agent_response: str              # Agent响应
    tool_calls: List[Dict]           # 工具调用记录
    scores: List[MetricScore]        # 评分明细
    overall_score: float             # 综合分数
    latency_ms: float                # 延迟
    token_usage: Dict[str, int]      # Token使用
    success: bool                    # 是否成功
```

#### BenchmarkResult

基准测试结果数据模型。

```python
@dataclass
class BenchmarkResult:
    id: str                          # 基准测试ID
    results: List[EvaluationResult]  # 所有结果
    total_tests: int                 # 总测试数
    passed_tests: int                # 通过数
    average_score: float             # 平均分数
    dimension_scores: Dict[str, float] # 各维度分数
    duration_seconds: float          # 总耗时
```

---

## 数据流设计

### 评估流程

```
用户输入
    ↓
创建TestCase
    ↓
选择适配器(Adapter)
    ↓
执行Agent获取响应
    ↓
收集工具调用信息
    ↓
执行所有评估器(Evaluators)
    ↓
计算各维度分数
    ↓
聚合生成EvaluationResult
    ↓
返回评估结果
```

### 批量评估流程

```
测试数据集
    ↓
创建多个TestCase
    ↓
并发执行评估(带信号量控制)
    ↓
收集所有EvaluationResult
    ↓
聚合统计分析
    ↓
生成BenchmarkResult
    ↓
输出报告
```

---

## 扩展机制

### 1. 自定义评估器

```python
from agenteval.evaluators import BaseEvaluator, MetricScore

class MyCustomEvaluator(BaseEvaluator):
    """自定义评估器示例"""
    
    async def evaluate(self, test_case, agent_response, context):
        # 实现你的评估逻辑
        score = self._calculate_score(agent_response)
        return MetricScore(name="custom", score=score)
```

### 2. 自定义适配器

```python
from agenteval.adapters import BaseAdapter, AgentResponse

class MyFrameworkAdapter(BaseAdapter):
    """自定义适配器示例"""
    
    FRAMEWORK_NAME = "my_framework"
    
    async def run_single_turn(self, message, context=None, tools=None):
        # 调用你的Agent
        response = await my_agent.arun(message)
        return AgentResponse(content=response)
```

### 3. 插件系统

```python
from agenteval.plugins import register_evaluator, register_adapter

@register_evaluator("my_evaluator")
class MyEvaluator(BaseEvaluator):
    ...

@register_adapter("my_adapter")
class MyAdapter(BaseAdapter):
    ...
```

---

## 设计决策

### 1. 为什么选择分层架构？

| 决策 | 理由 |
|------|------|
| 关注点分离 | 每层专注单一职责，降低复杂度 |
| 可扩展性 | 每层可独立扩展，不影响其他层 |
| 可测试性 | 每层可独立测试，提高测试效率 |
| 可维护性 | 修改影响范围可控，降低维护成本 |

### 2. 为什么使用适配器模式？

| 决策 | 理由 |
|------|------|
| 框架无关 | 统一接口屏蔽框架差异 |
| 渐进支持 | 逐步添加框架支持 |
| 社区贡献 | 降低贡献门槛 |
| 灵活扩展 | 支持自定义适配器 |

### 3. 为什么评估器独立设计？

| 决策 | 理由 |
|------|------|
| 灵活组合 | 按需选择评估器 |
| 易于扩展 | 自定义评估器简单 |
| 并行执行 | 评估器可并发运行 |
| 可插拔 | 支持动态添加移除 |

### 4. 为什么支持简单和高级两种模式？

| 决策 | 理由 |
|------|------|
| 降低门槛 | 初学者快速上手 |
| 保留灵活 | 专家可深度定制 |
| 渐进学习 | 从简单到高级平滑过渡 |
| 覆盖更广 | 满足不同用户需求 |

---

## 性能考量

### 并发控制

```python
# 使用asyncio实现异步评估
# 信号量控制并发数量
semaphore = asyncio.Semaphore(max_concurrency)

async def evaluate_with_semaphore(test_case):
    async with semaphore:
        return await evaluate_single(test_case)
```

### 内存管理

- **流式处理**：大批量测试分批加载
- **结果懒加载**：按需加载评估结果
- **及时释放**：评估完成后释放中间数据

### 性能优化

- **缓存机制**：缓存LLM评估结果
- **批量调用**：批量调用LLM API
- **异步执行**：充分利用IO等待时间

---

## 安全设计

### API Key管理

```python
# 环境变量存储
import os
api_key = os.getenv("OPENAI_API_KEY")

# 不写入日志
logger.info(f"Using API key: {api_key[:8]}...")

# 支持密钥轮换
def rotate_api_key(new_key):
    os.environ["OPENAI_API_KEY"] = new_key
```

### 数据安全

- **本地评估**：评估数据不上传云端
- **匿名化处理**：支持PII信息脱敏
- **可配置保留**：数据保留策略可配置

### 输入验证

- **参数校验**：严格验证输入参数
- **类型检查**：使用类型注解和检查
- **边界测试**：处理边界情况

---

## 未来规划

### v0.2.0 计划

- [ ] 更多评估器（代码生成、多模态）
- [ ] 更多适配器（Semantic Kernel、Haystack）
- [ ] 评估报告可视化
- [ ] 云端评估服务

### v0.3.0 计划

- [ ] 评估结果对比分析
- [ ] Agent性能排行榜
- [ ] 评估数据集市场
- [ ] 企业级功能

---

## 参考资料

- [Agent Evaluation Best Practices](https://docs.agenteval.dev)
- [LLM Evaluation Metrics](https://arxiv.org/abs/2307.03109)
- [Agent Benchmarking Survey](https://arxiv.org/abs/2308.03688)

---

**文档版本**: v1.0.0
**最后更新**: 2026-03-25
