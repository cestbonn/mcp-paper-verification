# 部署到GitHub指南

## 准备发布

### 1. 初始化Git仓库
```bash
cd mcp-paper-verification
git init
git add .
git commit -m "Initial commit: MCP Paper Verification service"
```

### 2. 创建GitHub仓库
1. 访问 [GitHub](https://github.com/new)
2. 创建新仓库，命名为 `mcp-paper-verification`
3. 选择Public或Private
4. 不需要初始化README（我们已经有了）

### 3. 推送到GitHub
```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/mcp-paper-verification.git
git push -u origin main
```

## 项目结构检查

确保包含以下文件：
- ✅ `README.md` (中文文档)
- ✅ `README_EN.md` (英文文档)
- ✅ `LICENSE` (MIT许可证)
- ✅ `pyproject.toml` (项目配置)
- ✅ `.gitignore` (忽略文件配置)
- ✅ `src/` (源代码目录)
- ✅ `tests/` (测试目录)

## 发布标签

创建版本标签：
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## GitHub仓库设置建议

1. **描述**: "A comprehensive academic paper verification MCP server"
2. **主题标签**: `mcp`, `academic-papers`, `verification`, `python`, `markdown`
3. **许可证**: MIT License
4. **主要语言**: Python

## 发布到PyPI (可选)

如果想发布到PyPI供他人安装：

```bash
# 构建包
uv build

# 发布到PyPI (需要PyPI账号)
uv publish
```

## 文档网站 (可选)

可以启用GitHub Pages来托管文档：
1. 在仓库设置中启用GitHub Pages
2. 选择 `README_EN.md` 作为主页

---

**注意**: 发布前请确保：
- 已测试所有功能正常工作
- 已更新API密钥示例（使用占位符）
- 已检查代码中没有硬编码的敏感信息 