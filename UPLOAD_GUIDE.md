# AgentEval GitHub仓库上传指南

## 前提条件
1. 已有GitHub账号
2. 已安装Git
3. 已配置Git凭证

## 步骤

### 1. 在GitHub上创建仓库

访问 https://github.com/new 并创建仓库：
- Repository name: AgentEval
- Description: 专为AI Agent设计的开源评估框架
- Visibility: Public
- 不要初始化README、.gitignore或License

### 2. 推送代码

打开命令行，执行以下命令（替换YOUR_USERNAME）：

```bash
cd E:\opencode项目\newthink\AgentEval
git remote add origin https://github.com/YOUR_USERNAME/AgentEval.git
git branch -M main
git push -u origin main
```

### 3. 验证

访问 https://github.com/YOUR_USERNAME/AgentEval 确认文件已上传

## 常见问题

### 认证问题
如果遇到认证问题，可以：
1. 使用Personal Access Token
2. 配置SSH Key
3. 使用GitHub CLI

### 推送失败
如果推送失败：
```bash
git pull --rebase origin main
git push -u origin main
```
