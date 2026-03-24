# 贡献指南 🤝

感谢你对AgentEval的兴趣！我们欢迎所有形式的贡献，无论是代码、文档、测试还是反馈。

---

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Pull Request流程](#pull-request流程)
- [问题反馈](#问题反馈)
- [社区](#社区)

---

## 🤝 行为准则

参与本项目即表示你同意遵守以下原则：

- 尊重所有参与者
- 使用包容性语言
- 接受建设性批评
- 关注社区利益
- 对其他社区成员表示同理心

---

## 🚀 如何贡献

### 报告问题

1. 检查[现有Issues](https://github.com/AgentEval/AgentEval/issues)是否已存在相同问题
2. 如果不存在，创建新Issue
3. 提供详细的问题描述，包括：
   - 问题描述
   - 复现步骤
   - 期望行为
   - 实际行为
   - 环境信息（Python版本、操作系统等）

### 提交代码

1. Fork项目到你的GitHub账号
2. 创建特性分支
3. 编写代码和测试
4. 提交Pull Request

### 改进文档

- 修复拼写错误
- 添加使用示例
- 改进文档结构
- 翻译文档

### 分享经验

- 在Issues中分享使用经验
- 编写博客文章
- 在社交媒体上分享

---

## 🛠️ 开发环境设置

### 前置要求

- Python 3.9+
- Git
- 虚拟环境工具（venv或conda）

### 设置步骤

```bash
# 1. Fork并克隆仓库
git clone https://github.com/your-username/AgentEval.git
cd AgentEval

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装开发依赖
pip install -e ".[dev]"

# 4. 安装pre-commit钩子
pre-commit install

# 5. 验证安装
pytest tests/
```

### 依赖说明

```
# 核心依赖
langchain>=0.1.0
openai>=1.0.0
anthropic>=0.18.0
pydantic>=2.0.0
asyncio

# 开发依赖
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
ruff>=0.1.0
mypy>=1.0.0
black>=23.0.0
pre-commit>=3.0.0
```

---

## 📝 代码规范

### Python风格

- 遵循[PEP 8](https://peps.python.org/pep-0008/)
- 使用类型注解
- 编写文档字符串
- 最大行长度：88字符（Black默认）

### 代码格式化

```bash
# 使用Black格式化代码
black agenteval/

# 使用Ruff检查代码
ruff check agenteval/

# 使用Mypy类型检查
mypy agenteval/
```

### 文档字符串

使用Google风格的文档字符串：

```python
def evaluate_single(
    self,
    test_case: TestCase,
    context: Optional[Dict[str, Any]] = None
) -> EvaluationResult:
    """执行单个测试用例评估。

    Args:
        test_case: 测试用例对象
        context: 额外的上下文信息

    Returns:
        EvaluationResult: 包含评估结果的对象

    Raises:
        AdapterError: 当适配器执行失败时
        TimeoutError: 当评估超时时

    Example:
        >>> result = await engine.evaluate_single(test_case)
        >>> print(result.overall_score)
    """
    pass
```

### 测试要求

- 每个新功能必须包含测试
- 测试覆盖率不低于80%
- 使用pytest编写测试

```python
import pytest
from agenteval import EvaluationEngine, TestCase

@pytest.mark.asyncio
async def test_evaluate_single():
    """测试单个评估功能"""
    engine = EvaluationEngine()
    test_case = TestCase(
        name="test",
        input_message="What is 2+2?",
        expected_output="4"
    )
    
    result = await engine.evaluate_single(test_case)
    
    assert result.success is True
    assert result.overall_score > 0
```

---

## 📋 提交规范

### Commit消息格式

使用[Conventional Commits](https://www.conventionalcommits.org/)规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type类型

| Type | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复bug |
| docs | 文档更新 |
| style | 代码格式（不影响功能） |
| refactor | 重构 |
| perf | 性能优化 |
| test | 测试相关 |
| chore | 构建/工具链相关 |
| ci | CI/CD相关 |

### 示例

```bash
# 新功能
git commit -m "feat(evaluators): add SafetyEvaluator"

# 修复bug
git commit -m "fix(adapter): handle timeout in LangChain adapter"

# 文档更新
git commit -m "docs: update API reference"

# 测试
git commit -m "test(core): add unit tests for EvaluationEngine"
```

---

## 🔄 Pull Request流程

### 1. 创建分支

```bash
# 从main分支创建特性分支
git checkout -b feature/my-feature

# 或修复分支
git checkout -b fix/my-fix
```

### 2. 开发和测试

```bash
# 编写代码
# ...

# 运行测试
pytest tests/

# 代码检查
ruff check agenteval/
mypy agenteval/
```

### 3. 提交更改

```bash
git add .
git commit -m "feat: add my feature"
```

### 4. 推送和创建PR

```bash
git push origin feature/my-feature
```

然后在GitHub上创建Pull Request。

### 5. PR模板

```markdown
## 描述
简要描述你的更改

## 更改类型
- [ ] 新功能
- [ ] Bug修复
- [ ] 文档更新
- [ ] 重构
- [ ] 测试

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 添加了相关测试
- [ ] 测试通过
- [ ] 更新了文档
- [ ] 添加了变更日志

## 相关Issue
Closes #123

## 截图（如适用）
```

### 6. 代码审查

- 至少需要1个维护者批准
- 所有CI检查必须通过
- 解决所有审查意见

---

## 🐛 问题反馈

### Bug报告

使用以下模板：

```markdown
**描述**
简要描述bug

**复现步骤**
1. 执行 '...'
2. 输入 '...'
3. 看到错误 '...'

**期望行为**
描述你期望发生的行为

**实际行为**
描述实际发生的行为

**环境信息**
- Python版本: [e.g., 3.11]
- AgentEval版本: [e.g., 0.1.0]
- 操作系统: [e.g., Ubuntu 22.04]

**附加信息**
添加任何其他相关信息
```

### 功能请求

使用以下模板：

```markdown
**功能描述**
简要描述你希望的功能

**使用场景**
描述这个功能的使用场景

**替代方案**
描述你考虑过的替代方案

**附加信息**
添加任何其他相关信息
```

---

## 🌐 社区

### 沟通渠道

- [GitHub Issues](https://github.com/AgentEval/AgentEval/issues)
- [GitHub Discussions](https://github.com/AgentEval/AgentEval/discussions)
- [Discord](https://discord.gg/agenteval)

### 贡献者

感谢所有为AgentEval做出贡献的人！

### 维护者

- @maintainer1
- @maintainer2

---

## 📄 许可证

通过贡献代码，你同意你的贡献将在[MIT License](LICENSE)下发布。

---

## 🙏 致谢

感谢以下项目和社区的启发：

- [LangChain](https://github.com/langchain-ai/langchain)
- [DeepEval](https://github.com/confident-ai/deepeval)
- [Pytest](https://github.com/pytest-dev/pytest)

---

**感谢你的贡献！** 🎉
