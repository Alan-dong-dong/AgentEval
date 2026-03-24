# AgentEval 🤖

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![GitHub Stars](https://img.shields.io/github/stars/AgentEval/AgentEval?style=social)](https://github.com/AgentEval/AgentEval)

> 专为AI Agent设计的开源评估框架，让Agent评估变得简单、可靠、可复现。

---

## ✨ 特性亮点

- 🎯 **Agent专用** - 三层评估架构，覆盖推理、行动、执行全链路
- 🔄 **可靠性测试** - 支持pass^k多轮一致性评估
- 💰 **成本效率** - 内置token消耗、延迟、成本综合评估
- 🔌 **框架无关** - 支持LangChain、CrewAI、AutoGen等主流框架
- 🚀 **简单易用** - 3行代码完成基础评估
- 🧩 **可扩展** - 插件系统，支持自定义评估器和适配器

---

## 🚀 快速开始

### 安装

```bash
pip install agenteval
```

### 30秒上手

```python
from agenteval import quick_eval

# 定义你的Agent
def my_agent(prompt: str) -> str:
    return "The answer is 4"

# 一行代码评估
result = quick_eval(my_agent, "What is 2+2?", expected="4")
print(f"Score: {result['score']:.2f}")
```

### 高级用法

```python
from agenteval import EvaluationEngine, TestCase
from agenteval.evaluators import CorrectnessEvaluator, ToolUsageEvaluator

# 创建评估引擎
engine = EvaluationEngine()

# 添加评估器
engine.add_evaluators([
    CorrectnessEvaluator(),
    ToolUsageEvaluator()
])

# 创建测试用例
test_case = TestCase(
    name="simple_qa",
    input_message="What is the capital of France?",
    expected_output="Paris"
)

# 运行评估
result = await engine.evaluate_single(test_case)
print(f"Overall Score: {result.overall_score:.2f}")
```

---

## 🏗️ 三层评估架构

```
┌─────────────────────────────────────────────┐
│              推理层 (Reasoning)              │
│  计划质量 | 计划遵循度 | 推理逻辑            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│              行动层 (Action)                 │
│  工具选择 | 参数正确性 | 调用准确性          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│              执行层 (Execution)              │
│  任务完成度 | 执行效率 | 资源消耗            │
└─────────────────────────────────────────────┘
```

---

## 📦 内置评估器

| 评估器 | 评估维度 | 适用场景 |
|--------|----------|----------|
| `CorrectnessEvaluator` | 功能正确性 | 所有Agent类型 |
| `ToolUsageEvaluator` | 工具使用准确性 | 使用工具的Agent |
| `EfficiencyEvaluator` | 响应效率 | 性能敏感场景 |
| `SafetyEvaluator` | 安全合规 | 生产环境部署 |
| `ConversationEvaluator` | 对话质量 | 对话型Agent |

---

## 🔌 支持的框架

- ✅ **LangChain** / LangGraph
- ✅ **CrewAI**
- ✅ **AutoGen**
- ✅ **LlamaIndex**
- ✅ **自定义Agent** (Callable接口)

---

## 📚 文档

- [快速开始](docs/QUICKSTART.md)
- [架构设计](ARCHITECTURE.md)
- [API参考](API_REFERENCE.md)
- [评估器指南](guides/EVALUATORS_GUIDE.md)
- [适配器开发](guides/ADAPTERS_GUIDE.md)
- [使用示例](guides/EXAMPLES.md)

---

## 🛠️ CLI 命令行

```bash
# 快速评估
agenteval quick mymodule.my_agent "What is 2+2?" --expected "4"

# 运行评估套件
agenteval run eval_config.yaml --output results.json

# 使用预设数据集
agenteval preset mymodule.my_agent --dataset basic_qa

# 生成报告
agenteval report results.json --format html --output report.html
```

---

## 🧪 预设数据集

```python
from agenteval.simple.presets import PresetDatasets

# 获取预设数据集
basic_qa = PresetDatasets.get_basic_qa()        # 基础问答
tool_use = PresetDatasets.get_tool_use_tests()  # 工具使用
safety = PresetDatasets.get_safety_tests()      # 安全测试
conversation = PresetDatasets.get_conversation_tests()  # 对话测试
```

---

## 📊 评估报告示例

```
╔════════════════════════════════════════════════════════════╗
║                  AgentEval 评估报告                        ║
╠════════════════════════════════════════════════════════════╣
║  测试总数: 50      通过: 45      失败: 5                   ║
║  平均分数: 0.89    总耗时: 12.5s                          ║
╠════════════════════════════════════════════════════════════╣
║  维度得分:                                                 ║
║  ├── 正确性:     0.92 ████████████████░░░░                ║
║  ├── 工具使用:   0.85 ███████████████░░░░░                ║
║  ├── 效率:       0.91 ████████████████░░░░                ║
║  └── 安全:       0.95 █████████████████░░                 ║
╠════════════════════════════════════════════════════════════╣
║  性能统计:                                                 ║
║  ├── 平均延迟:   245ms                                    ║
║  ├── 平均Token:  350                                      ║
║  └── Pass^3:     0.87                                     ║
╚════════════════════════════════════════════════════════════╝
```

---

## 🤝 贡献

我们欢迎所有形式的贡献！请查看 [贡献指南](CONTRIBUTING.md)。

### 如何贡献

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 贡献者

感谢所有为AgentEval做出贡献的人！

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

## 🔗 相关链接

- [GitHub仓库](https://github.com/AgentEval/AgentEval)
- [PyPI包](https://pypi.org/project/agenteval/)
- [文档站点](https://agenteval.github.io)
- [问题反馈](https://github.com/AgentEval/AgentEval/issues)

---

## 💡 为什么选择AgentEval？

| 痛点 | AgentEval解决方案 |
|------|-------------------|
| 基准测试与生产差距37% | 三层评估架构，覆盖真实场景 |
| 缺乏Agent专用工具 | 专为Agent设计的评估指标 |
| 多框架支持困难 | 框架无关，统一接口 |
| 评估门槛高 | 简单模式，3行代码上手 |
| 可靠性难保证 | pass^k多轮一致性测试 |

---

**让Agent评估变得简单、可靠、可复现！** 🚀
