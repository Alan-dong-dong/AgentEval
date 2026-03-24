# 使用示例 📚

## 目录

- [基础示例](#基础示例)
- [高级示例](#高级示例)
- [框架集成](#框架集成)
- [CI/CD集成](#cicd集成)
- [最佳实践](#最佳实践)

---

## 基础示例

### 示例1：评估简单问答Agent

最简单的评估方式，一行代码完成。

```python
from agenteval import quick_eval

# 定义你的Agent
def qa_agent(question: str) -> str:
    """简单的问答Agent"""
    if "capital" in question.lower() and "france" in question.lower():
        return "The capital of France is Paris."
    return "I don't know the answer."

# 评估
result = quick_eval(qa_agent, "What is the capital of France?")

print(f"Score: {result['score']:.2f}")
print(f"Response: {result['response']}")
print(f"Latency: {result['latency_ms']:.2f}ms")
```

**输出：**
```
Score: 0.95
Response: The capital of France is Paris.
Latency: 12.34ms
```

---

### 示例2：带期望输出的评估

```python
from agenteval import quick_eval

def math_agent(question: str) -> str:
    """数学问答Agent"""
    if "2+2" in question or "2 + 2" in question:
        return "4"
    return "I don't know."

# 带期望输出
result = quick_eval(
    math_agent,
    "What is 2+2?",
    expected="4"
)

print(f"Score: {result['score']:.2f}")
print(f"Correct: {result['score'] >= 0.8}")
```

---

### 示例3：使用EvaluationEngine

```python
import asyncio
from agenteval import EvaluationEngine, TestCase
from agenteval.evaluators import CorrectnessEvaluator, EfficiencyEvaluator

async def main():
    # 创建评估引擎
    engine = EvaluationEngine()
    
    # 添加评估器
    engine.add_evaluators([
        CorrectnessEvaluator(model="gpt-4"),
        EfficiencyEvaluator(latency_threshold_ms=3000)
    ])
    
    # 定义Agent
    def my_agent(prompt: str) -> str:
        return "The answer is 42"
    
    # 创建适配器
    from agenteval.adapters import CallableAdapter
    from agenteval.models import AgentConfig
    
    config = AgentConfig(
        framework="callable",
        agent_callable=my_agent
    )
    adapter = CallableAdapter(config)
    engine.set_adapter(adapter)
    
    # 创建测试用例
    test_case = TestCase(
        name="meaning_of_life",
        input_message="What is the meaning of life?",
        expected_output="42"
    )
    
    # 运行评估
    result = await engine.evaluate_single(test_case)
    
    print(f"Overall Score: {result.overall_score:.2f}")
    print(f"Latency: {result.latency_ms:.2f}ms")
    print(f"Success: {result.success}")
    
    for score in result.scores:
        print(f"  {score.name}: {score.score:.2f}")

# 运行
asyncio.run(main())
```

---

### 示例4：批量评估

```python
import asyncio
from agenteval import EvaluationEngine, TestCase
from agenteval.evaluators import CorrectnessEvaluator
from agenteval.adapters import CallableAdapter
from agenteval.models import AgentConfig

async def main():
    # 创建Agent
    def qa_agent(prompt: str) -> str:
        answers = {
            "2+2": "4",
            "3+3": "6",
            "4*4": "16"
        }
        for key, value in answers.items():
            if key in prompt:
                return value
        return "I don't know."
    
    # 配置引擎
    engine = EvaluationEngine()
    engine.add_evaluator(CorrectnessEvaluator())
    
    config = AgentConfig(
        framework="callable",
        agent_callable=qa_agent
    )
    engine.set_adapter(CallableAdapter(config))
    
    # 创建测试用例
    test_cases = [
        TestCase(name="math1", input_message="What is 2+2?", expected_output="4"),
        TestCase(name="math2", input_message="What is 3+3?", expected_output="6"),
        TestCase(name="math3", input_message="What is 4*4?", expected_output="16"),
        TestCase(name="math4", input_message="What is 5*5?", expected_output="25"),
    ]
    
    # 批量评估
    result = await engine.evaluate_batch(test_cases)
    
    print(f"Total Tests: {result.total_tests}")
    print(f"Passed: {result.passed_tests}")
    print(f"Failed: {result.failed_tests}")
    print(f"Average Score: {result.average_score:.2f}")
    print(f"Duration: {result.duration_seconds:.2f}s")

asyncio.run(main())
```

**输出：**
```
Total Tests: 4
Passed: 3
Failed: 1
Average Score: 0.75
Duration: 0.45s
```

---

## 高级示例

### 示例5：使用预设数据集

```python
import asyncio
from agenteval import EvaluationEngine
from agenteval.simple.presets import PresetDatasets
from agenteval.adapters import CallableAdapter
from agenteval.models import AgentConfig

async def main():
    # 获取预设数据集
    test_cases = PresetDatasets.get_basic_qa()
    
    print(f"Loaded {len(test_cases)} test cases")
    for tc in test_cases:
        print(f"  - {tc.name}: {tc.input_message[:50]}...")
    
    # 配置引擎
    engine = EvaluationEngine()
    
    def my_agent(prompt: str) -> str:
        # 你的Agent逻辑
        return "This is a test response"
    
    config = AgentConfig(
        framework="callable",
        agent_callable=my_agent
    )
    engine.set_adapter(CallableAdapter(config))
    
    # 运行评估
    result = await engine.evaluate_batch(test_cases)
    
    print(f"\nResults:")
    print(f"  Average Score: {result.average_score:.2f}")
    print(f"  Passed: {result.passed_tests}/{result.total_tests}")

asyncio.run(main())
```

---

### 示例6：自定义评估器

```python
import asyncio
from agenteval import EvaluationEngine, TestCase
from agenteval.evaluators import BaseEvaluator, MetricScore
from agenteval.adapters import CallableAdapter
from agenteval.models import AgentConfig

class LengthEvaluator(BaseEvaluator):
    """评估响应长度的自定义评估器"""
    
    def __init__(self, min_length=10, max_length=1000, config=None):
        super().__init__(config)
        self.min_length = min_length
        self.max_length = max_length
        self.name = "LengthEvaluator"
    
    async def evaluate(self, test_case, agent_response, context):
        length = len(agent_response)
        
        if length < self.min_length:
            score = 0.5
            details = f"Response too short ({length} < {self.min_length})"
        elif length > self.max_length:
            score = 0.7
            details = f"Response too long ({length} > {self.max_length})"
        else:
            score = 1.0
            details = f"Response length OK ({length})"
        
        return MetricScore(
            name=self.name,
            score=score,
            weight=1.0,
            details=details,
            metadata={"length": length}
        )

async def main():
    # 配置引擎
    engine = EvaluationEngine()
    engine.add_evaluator(LengthEvaluator(min_length=5, max_length=100))
    
    def my_agent(prompt: str) -> str:
        return "Short response"
    
    config = AgentConfig(
        framework="callable",
        agent_callable=my_agent
    )
    engine.set_adapter(CallableAdapter(config))
    
    # 运行评估
    test_case = TestCase(name="test", input_message="Hello")
    result = await engine.evaluate_single(test_case)
    
    print(f"Score: {result.overall_score:.2f}")
    for score in result.scores:
        print(f"  {score.name}: {score.score:.2f} - {score.details}")

asyncio.run(main())
```

---

## 框架集成

### 示例7：集成LangChain Agent

```python
import asyncio
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_agent
from langchain.tools import Tool
from agenteval import EvaluationEngine, TestCase
from agenteval.adapters import LangChainAdapter
from agenteval.models import AgentConfig

async def main():
    # 创建LangChain Agent
    llm = ChatOpenAI(model="gpt-4")
    
    tools = [
        Tool(
            name="Calculator",
            func=lambda x: eval(x),
            description="Useful for math calculations"
        )
    ]
    
    agent = create_openai_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)
    
    # 配置AgentEval
    config = AgentConfig(
        framework="langchain",
        agent_instance=agent_executor
    )
    adapter = LangChainAdapter(config)
    
    engine = EvaluationEngine()
    engine.set_adapter(adapter)
    
    # 运行评估
    test_case = TestCase(
        name="calculation",
        input_message="What is 15 * 7?",
        expected_output="105"
    )
    
    result = await engine.evaluate_single(test_case)
    print(f"Score: {result.overall_score:.2f}")

asyncio.run(main())
```

---

### 示例8：集成CrewAI

```python
import asyncio
from crewai import Agent, Task, Crew
from agenteval import EvaluationEngine, TestCase
from agenteval.adapters import CrewAIAdapter
from agenteval.models import AgentConfig

async def main():
    # 创建CrewAI Agent
    researcher = Agent(
        role="Researcher",
        goal="Research topics thoroughly",
        backstory="You are an expert researcher",
        verbose=True
    )
    
    writer = Agent(
        role="Writer",
        goal="Write clear summaries",
        backstory="You are a skilled writer",
        verbose=True
    )
    
    crew = Crew(agents=[researcher, writer])
    
    # 配置AgentEval
    config = AgentConfig(
        framework="crewai",
        agent_instance=crew
    )
    adapter = CrewAIAdapter(config)
    
    engine = EvaluationEngine()
    engine.set_adapter(adapter)
    
    # 运行评估
    test_case = TestCase(
        name="research",
        input_message="Research the latest AI trends"
    )
    
    result = await engine.evaluate_single(test_case)
    print(f"Score: {result.overall_score:.2f}")

asyncio.run(main())
```

---

## CI/CD集成

### 示例9：GitHub Actions集成

创建 `.github/workflows/agent-eval.yml`：

```yaml
name: Agent Evaluation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install agenteval
          pip install -r requirements.txt
      
      - name: Run evaluation
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          agenteval run eval_config.yaml --output results.json
      
      - name: Check results
        run: |
          python -c "
          import json
          import sys
          
          with open('results.json') as f:
              results = json.load(f)
          
          if results['average_score'] < 0.8:
              print(f'Evaluation failed: {results[\"average_score\"]:.2f} < 0.8')
              sys.exit(1)
          
          print(f'Evaluation passed: {results[\"average_score\"]:.2f}')
          "
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: evaluation-results
          path: results.json
```

---

### 示例10：预提交钩子

创建 `.pre-commit-config.yaml`：

```yaml
repos:
  - repo: local
    hooks:
      - id: agent-eval
        name: Agent Evaluation
        entry: agenteval run eval_config.yaml
        language: system
        files: '\.py$'
        pass_filenames: false
```

---

## 最佳实践

### 1. 从简单开始

```python
# 第一步：使用quick_eval验证基本功能
result = quick_eval(my_agent, "Hello")

# 第二步：使用EvaluationEngine进行深度评估
engine = EvaluationEngine()
result = await engine.evaluate_single(test_case)

# 第三步：批量评估
result = await engine.evaluate_batch(test_cases)
```

### 2. 使用预设数据集

```python
# 快速建立基准
test_cases = PresetDatasets.get_basic_qa()
result = await engine.evaluate_batch(test_cases)
```

### 3. 自定义评估器

```python
# 针对特定场景优化
class MyEvaluator(BaseEvaluator):
    async def evaluate(self, test_case, agent_response, context):
        # 实现你的评估逻辑
        score = self._my_scoring_logic(agent_response)
        return MetricScore(name="custom", score=score)
```

### 4. 集成CI/CD

```yaml
# 自动化评估流程
- name: Run evaluation
  run: agenteval run eval_config.yaml
```

### 5. 监控和改进

```python
# 定期运行评估
result = await engine.evaluate_batch(test_cases)

# 分析结果
for r in result.results:
    if not r.success:
        print(f"Failed: {r.test_case_id}")
        print(f"Error: {r.error_message}")
```

---

**文档版本**: v1.0.0
**最后更新**: 2026-03-25
