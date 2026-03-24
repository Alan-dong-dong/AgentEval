# 更新日志 📋

所有重要变更都将记录在此文件。

格式基于[Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本遵循[语义化版本](https://semver.org/lang/zh-CN/)。

---

## [Unreleased]

### Added
- 初始项目结构
- 核心评估引擎 (EvaluationEngine)
- 基础评估器
  - CorrectnessEvaluator: 功能正确性评估
  - ToolUsageEvaluator: 工具使用准确性评估
  - EfficiencyEvaluator: 响应效率评估
  - SafetyEvaluator: 安全合规评估
  - ConversationEvaluator: 对话质量评估
- 框架适配器
  - LangChainAdapter: LangChain/LangGraph支持
  - CrewAIAdapter: CrewAI支持
  - AutoGenAdapter: AutoGen支持
  - CallableAdapter: 通用Callable接口
- 简单模式API (quick_eval)
- 预设数据集
  - basic_qa: 基础问答测试集
  - tool_use: 工具使用测试集
  - safety: 安全测试集
  - conversation: 对话测试集
- 插件系统
- CLI命令行工具
- 完整文档
  - README.md: 项目介绍
  - ARCHITECTURE.md: 技术架构
  - API_REFERENCE.md: API参考
  - CONTRIBUTING.md: 贡献指南
  - EVALUATORS_GUIDE.md: 评估器指南
  - ADAPTERS_GUIDE.md: 适配器指南
  - EXAMPLES.md: 使用示例

### Changed
- 无

### Deprecated
- 无

### Removed
- 无

### Fixed
- 无

### Security
- 无

---

## [0.1.0] - 2026-03-25

### Added
- 🎉 首次发布
- 完整的Agent评估框架
- 三层评估架构（推理层、行动层、执行层）
- 支持pass^k可靠性测试
- 内置成本效率评估
- 框架无关设计
- 简单模式和高级模式
- 完整的文档和示例

---

## 版本说明

### 版本号格式

- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 变更类型

- **Added**: 新功能
- **Changed**: 对现有功能的变更
- **Deprecated**: 已经不建议使用，即将移除的功能
- **Removed**: 已移除的功能
- **Fixed**: 任何bug修复
- **Security**: 安全相关的修复和改进

---

## 贡献者

感谢所有为AgentEval做出贡献的人！

<!-- 贡献者列表将在项目发展后更新 -->

---

## 链接

- [GitHub仓库](https://github.com/AgentEval/AgentEval)
- [PyPI包](https://pypi.org/project/agenteval/)
- [文档站点](https://agenteval.github.io)
- [问题反馈](https://github.com/AgentEval/AgentEval/issues)

---

**维护者**: AgentEval Team
