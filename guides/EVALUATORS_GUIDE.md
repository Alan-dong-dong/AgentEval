# 评估器使用指南 📊

## 目录

- [概述](#概述)
- [内置评估器](#内置评估器)
- [使用方法](#使用方法)
- [自定义评估器](#自定义评估器)
- [评估器组合](#评估器组合)
- [最佳实践](#最佳实践)

---

## 概述

评估器是AgentEval的核心组件，负责从不同维度评估Agent的输出质量。每个评估器专注一个特定的评估维度，可以灵活组合使用。

### 评估器类型

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| RuleBasedEvaluator | 基于规则的评估 | 确定性评估 |
| LLMBasedEvaluator | 基于LLM的评估 | 主观质量评估 |
| CustomEvaluator | 自定义评估 | 特定需求 |

### 三层评估架构

```
推理层 (Reasoning)
├── PlanQualityMetric: 计划质量
└── PlanAdherenceMetric: 计划遵循度

行动层 (Action)
├── ToolCorrectnessMetric: 工具选择正确性
└── ArgumentCorrectnessMetric: 参数正确性

执行层 (Execution)
├── TaskCompletionMetric: 任务完成度
└── StepEfficiencyMetric: 执行效率
```

---

## 内置评估器

### CorrectnessEvaluator

**评估维度**：功能正确性
**适用场景**：所有Agent类型

评估Agent是否正确理解并完成了用户请求的任务。

```python
from agenteval.evaluators import CorrectnessEvaluator

evaluator = CorrectnessEvaluator(
    model="gpt-4",           # 用于评估的LLM模型
    threshold=0.7,           # 通过阈值
    weight=1.0,              # 权重
    strict_mode=False        # 严格模式
)
```

**评估指标：**
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
print(f"Details: {score.details}")
```

---

### ToolUsageEvaluator

**评估维度**：工具使用准确性
**适用场景**：使用工具的Agent

评估Agent是否正确选择了和使用了工具。

```python
from agenteval.evaluators import ToolUsageEvaluator

evaluator = ToolUsageEvaluator(
    strict_mode=False,          # 严格模式
    weight=0.8,                 # 权重
    allow_extra_tools=False     # 允许额外工具
)
```

**评估指标：**
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
print(f"F1 Score: {score.metadata['f1']:.2f}")
```

---

### EfficiencyEvaluator

**评估维度**：响应效率
**适用场景**：性能敏感场景

评估Agent的响应效率，包括延迟和资源消耗。

```python
from agenteval.evaluators import EfficiencyEvaluator

evaluator = EfficiencyEvaluator(
    latency_threshold_ms=5000,  # 延迟阈值
    token_threshold=1000,       # Token阈值
    weight=0.5                  # 权重
)
```

**评估指标：**
- 响应延迟
- Token消耗
- 成本效率

**评分标准：**

| 延迟 | 分数 |
|------|------|
| < 2s | 1.0 (优秀) |
| 2-5s | 0.8 (良好) |
| 5-10s | 0.6 (一般) |
| > 10s | 0.4 (较差) |

**示例：**

```python
from agenteval.evaluators import EfficiencyEvaluator

evaluator = EfficiencyEvaluator(latency_threshold_ms=3000)
score = await evaluator.evaluate(test_case, agent_response, context)

print(f"Efficiency Score: {score.score:.2f}")
print(f"Latency: {score.metadata['latency_ms']:.2f}ms")
print(f"Tokens: {score.metadata['token_usage']}")
```

---

### SafetyEvaluator

**评估维度**：安全合规
**适用场景**：生产环境部署

评估Agent的输出是否符合安全和合规要求。

```python
from agenteval.evaluators import SafetyEvaluator

evaluator = SafetyEvaluator(
    categories=["harmful", "bias", "privacy"],  # 评估类别
    weight=1.0                                   # 权重
)
```

**评估类别：**
- harmful: 有害内容
- bias: 偏见检测
- privacy: 隐私保护
- policy: 政策合规

**示例：**

```python
from agenteval.evaluators import SafetyEvaluator

evaluator = SafetyEvaluator(categories=["harmful", "bias"])
score = await evaluator.evaluate(test_case, agent_response, context)

print(f"Safety Score: {score.score:.2f}")
print(f"Categories: {score.metadata['categories']}")
```

---

### ConversationEvaluator

**评估维度**：对话质量
**适用场景**：对话型Agent

评估Agent在多轮对话中的表现。

```python
from agenteval.evaluators import ConversationEvaluator

evaluator = ConversationEvaluator(
    model="gpt-4",              # 用于评估的LLM模型
    weight=0.8                  # 权重
)
```

**评估指标：**
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
print(f"Context Retention: {score.metadata['context_retention']:.2f}")
```

---

## 使用方法

### 基础使用

```python
from agenteval import EvaluationEngine
from agenteval.evaluators import CorrectnessEvaluator, ToolUsageEvaluator

# 创建评估引擎
engine = EvaluationEngine()

# 添加评估器
engine.add_evaluator(CorrectnessEvaluator())
engine.add_evaluator(ToolUsageEvaluator())

# 运行评估
result = await engine.evaluate_single(test_case)
```

### 配置评估器

```python
from agenteval.evaluators import CorrectnessEvaluator

# 使用不同配置
evaluator = CorrectnessEvaluator(
    model="gpt-4",           # 使用GPT-4评估
    threshold=0.8,           # 更高阈值
    weight=1.5,              # 更高权重
    strict_mode=True         # 严格模式
)
```

### 批量添加评估器

```python
from agenteval.evaluators import (
    CorrectnessEvaluator,
    ToolUsageEvaluator,
    EfficiencyEvaluator,
    SafetyEvaluator
)

engine.add_evaluators([
    CorrectnessEvaluator(weight=1.0),
    ToolUsageEvaluator(weight=0.8),
    EfficiencyEvaluator(weight=0.5),
    SafetyEvaluator(weight=1.0)
])
```

---

## 自定义评估器

### 基于规则的评估器

```python
from agenteval.evaluators import BaseEvaluator, MetricScore
from agenteval.models import TestCase

class KeywordEvaluator(BaseEvaluator):
    """基于关键词的评估器"""
    
    def __init__(self, keywords: list, config=None):
        super().__init__(config)
        self.keywords = keywords
        self.name = "KeywordEvaluator"
    
    async def evaluate(self, test_case, agent_response, context):
        # 计算关键词命中率
        hits = sum(1 for kw in self.keywords if kw.lower() in agent_response.lower())
        score = hits / len(self.keywords) if self.keywords else 0
        
        return MetricScore(
            name=self.name,
            score=score,
            weight=1.0,
            details=f"Hit {hits}/{len(self.keywords)} keywords",
            metadata={"hits": hits, "total": len(self.keywords)}
        )

# 使用
evaluator = KeywordEvaluator(keywords=["correct", "answer", "42"])
score = await evaluator.evaluate(test_case, agent_response, context)
```

### 基于LLM的评估器

```python
from agenteval.evaluators import LLMBasedEvaluator, MetricScore
import openai

class CustomLLMEvaluator(LLMBasedEvaluator):
    """自定义LLM评估器"""
    
    EVALUATION_PROMPT = """
    请评估以下Agent响应的质量。
    
    用户问题: {input}
    Agent响应: {response}
    
    评估标准:
    1. 准确性 (0-100)
    2. 完整性 (0-100)
    3. 清晰度 (0-100)
    
    请返回JSON格式:
    {{"accuracy": <score>, "completeness": <score>, "clarity": <score>}}
    """
    
    def __init__(self, model="gpt-4", config=None):
        super().__init__(config)
        self.model = model
        self.client = openai.AsyncOpenAI()
    
    async def evaluate(self, test_case, agent_response, context):
        prompt = self.EVALUATION_PROMPT.format(
            input=test_case.input_message,
            response=agent_response
        )
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        import json
        scores = json.loads(response.choices[0].message.content)
        
        # 计算平均分
        avg_score = sum(scores.values()) / (len(scores) * 100)
        
        return MetricScore(
            name="CustomLLMEvaluator",
            score=avg_score,
            weight=1.0,
            details=f"Scores: {scores}",
            metadata=scores
        )

# 使用
evaluator = CustomLLMEvaluator(model="gpt-4")
score = await evaluator.evaluate(test_case, agent_response, context)
```

### 注册自定义评估器

```python
from agenteval.plugins import register_evaluator

@register_evaluator("my_evaluator")
class MyEvaluator(BaseEvaluator):
    ...

# 之后可以这样使用
from agenteval.plugins import get_registry

registry = get_registry()
evaluator_class = registry.get_evaluator("my_evaluator")
evaluator = evaluator_class()
```

---

## 评估器组合

### 权重组合

```python
from agenteval import EvaluationEngine

engine = EvaluationEngine()

# 不同权重的评估器组合
engine.add_evaluators([
    CorrectnessEvaluator(weight=1.5),      # 最重要
    ToolUsageEvaluator(weight=1.0),        # 重要
    EfficiencyEvaluator(weight=0.5),       # 次要
    SafetyEvaluator(weight=1.2)            # 重要
])

# 综合分数 = Σ(score * weight) / Σ(weight)
```

### 条件评估

```python
from agenteval.evaluators import BaseEvaluator, MetricScore

class ConditionalEvaluator(BaseEvaluator):
    """条件评估器"""
    
    def __init__(self, evaluators: dict, config=None):
        """
        evaluators: {
            "tool_use": ToolUsageEvaluator(),
            "no_tool": CorrectnessEvaluator()
        }
        """
        super().__init__(config)
        self.evaluators = evaluators
    
    async def evaluate(self, test_case, agent_response, context):
        # 根据条件选择评估器
        if context.get("tool_calls"):
            evaluator = self.evaluators["tool_use"]
        else:
            evaluator = self.evaluators["no_tool"]
        
        return await evaluator.evaluate(test_case, agent_response, context)
```

---

## 最佳实践

### 1. 选择合适的评估器

| 场景 | 推荐评估器 |
|------|-----------|
| 简单问答 | CorrectnessEvaluator |
| 工具使用 | ToolUsageEvaluator + CorrectnessEvaluator |
| 对话系统 | ConversationEvaluator |
| 生产部署 | SafetyEvaluator + EfficiencyEvaluator |
| 全面评估 | 所有评估器组合 |

### 2. 调整权重

根据业务需求调整评估器权重：

```python
# 重视准确性
engine.add_evaluators([
    CorrectnessEvaluator(weight=2.0),
    EfficiencyEvaluator(weight=0.5)
])

# 重视效率
engine.add_evaluators([
    CorrectnessEvaluator(weight=1.0),
    EfficiencyEvaluator(weight=1.5)
])
```

### 3. 使用适当的阈值

```python
# 严格阈值（生产环境）
evaluator = CorrectnessEvaluator(threshold=0.9)

# 宽松阈值（开发环境）
evaluator = CorrectnessEvaluator(threshold=0.7)
```

### 4. 监控评估器性能

```python
import time

start = time.time()
score = await evaluator.evaluate(test_case, agent_response, context)
elapsed = time.time() - start

print(f"Evaluation took {elapsed:.2f}s")
```

---

## 常见问题

### Q: 如何选择评估模型？

A: 推荐使用与被评估Agent相同或更强的模型。例如：
- Agent使用GPT-4 → 评估使用GPT-4
- Agent使用GPT-3.5 → 评估使用GPT-4

### Q: 评估器可以并行执行吗？

A: 可以。AgentEval支持评估器并行执行：

```python
engine = EvaluationEngine(config={"max_concurrency": 5})
```

### Q: 如何降低评估成本？

A: 
1. 使用更小的评估模型
2. 启用缓存
3. 减少评估器数量
4. 使用规则评估器替代LLM评估器

---

**文档版本**: v1.0.0
**最后更新**: 2026-03-25
