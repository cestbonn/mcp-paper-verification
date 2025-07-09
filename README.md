# MCP Paper Verification

一个全面的学术论文验证MCP服务，用于检查Markdown格式论文的各种问题和不规范之处。

## 功能特性

### 🔍 验证项目

1. **罗列情况检查**
   - 检测段落是否过短或过于稀疏
   - 识别列表式内容模式
   - 计算内容密度和稀疏度得分

2. **刻板印象检查**
   - 检测常见的学术模板用语（如"首先，"、"其次，"等）
   - 识别过度使用的加粗标题模式
   - 分析表达方式的多样性

3. **LaTeX公式格式检查**
   - 检测未包装的希腊字母和数学符号
   - 确保数学表达式使用proper LaTeX格式
   - 验证公式的Markdown兼容性

4. **文献引用检查**
   - 验证引用格式是否为标准的`[@key]`格式
   - 检查引用键是否在bib文件中存在
   - 统计引用数量和唯一性

5. **图片链接检查**
   - 确保使用绝对路径而非相对路径或网络链接
   - 验证图片文件是否实际存在
   - 检查图片引用格式

6. **代码块检查**
   - 检测并报告任何代码块（学术论文中不应包含）
   - 包括围栏代码块、行内代码和缩进代码块

7. **引用数量统计**
   - 统计论文中的独立引用数量
   - 根据学术标准检查（默认：15个以上引用）
   - 提供智能警告和上下文感知的建议
   - 处理各种论文类型和特殊要求

8. **参考文献真实性验证**
   - 通过Google Serper API搜索验证参考文献是否真实存在
   - 检查bib文件格式和完整性
   - 提供验证统计

## 安装和配置

### 前提条件

- Python 3.10+
- 有效的Serper API密钥（用于参考文献验证）

### 安装

1. 克隆或下载项目到本地
2. 进入项目目录：
   ```bash
   cd mcp-paper-verification
   ```

3. 使用uv安装依赖：
   ```bash
   uv install
   ```

### 环境配置

设置Serper API密钥：
```bash
export SERPER_API_KEY="your_serper_api_key_here"
```

或者在`.env`文件中设置：
```
SERPER_API_KEY=your_serper_api_key_here
```

## 使用方法

### 作为MCP服务器启动

```bash
uv run mcp-paper-verification
```

### MCP客户端配置

#### Claude Desktop配置

在`~/.config/claude-desktop/claude_desktop_config.json`中添加：

```json
{
  "mcpServers": {
    "mcp-paper-verification": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-paper-verification", "run", "mcp-paper-verification"],
      "env": {
        "SERPER_API_KEY": "your_serper_api_key_here"
      }
    }
  }
}
```

#### Cherry Studio配置

```json
{
  "name": "mcp-paper-verification",
  "serverName": "PaperVerificationServer",
  "command": "uv",
  "args": ["--directory", "/path/to/mcp-paper-verification", "run", "mcp-paper-verification"],
  "env": {
    "SERPER_API_KEY": "your_serper_api_key_here"
  }
}
```

### 可用工具

#### 1. `verify_paper_comprehensive`
综合验证论文的所有方面：
- **参数**：
  - `md_file_path`: Markdown论文文件路径
  - `bib_file_path`: BibTeX文件路径（可选）
  - `serper_api_key`: Serper API密钥（可选）
  - `generate_markdown_report`: 是否生成Markdown报告（默认：true）

#### 2. `verify_sparse_content_only`
仅检查内容稀疏情况：
- **参数**：
  - `md_file_path`: Markdown论文文件路径

#### 3. `verify_stereotype_content_only`
仅检查刻板印象表达：
- **参数**：
  - `md_file_path`: Markdown论文文件路径

#### 4. `verify_reference_count_only`
仅检查引用数量统计：
- **参数**：
  - `md_file_path`: Markdown论文文件路径
  - `min_references`: 建议的最少引用数量（默认：15）

#### 5. `verify_bib_references_only`
仅验证参考文献真实性：
- **参数**：
  - `bib_file_path`: BibTeX文件路径
  - `serper_api_key`: Serper API密钥（可选）

#### 6. `health_check`
健康检查服务状态

## 示例使用

### 在MCP客户端中调用

```
验证这篇论文：/path/to/paper.md，bib文件在：/path/to/references.bib
```

### 输出示例

验证完成后，服务会返回：

1. **验证摘要**：各项检查的通过/失败状态
2. **详细结果**：每项检查的具体问题列表
3. **Markdown报告**：格式化的详细报告，包含：
   - 问题的具体位置和描述
   - 修改建议
   - 统计信息

## 验证标准

### 高质量学术论文应该：

✅ **内容密度**：段落应有足够长度和实质内容  
✅ **表达多样性**：避免过度使用模板化表达  
✅ **格式规范**：数学公式使用标准LaTeX语法  
✅ **引用规范**：使用`[@key]`格式且在bib文件中存在  
✅ **引用数量**：适当的引用数量（完整论文通常需要15个以上）  
✅ **资源完整**：图片使用绝对路径且文件存在  
✅ **内容纯净**：不包含代码块等无关内容  
✅ **参考可靠**：引用的文献真实存在且可验证  

## API参考

详细的API文档请参考MCP工具定义，所有工具都遵循标准的MCP协议。

## 故障排除

### 常见问题

1. **Serper API错误**：确保API密钥正确且有足够配额
2. **文件路径问题**：使用绝对路径避免相对路径问题
3. **编码问题**：确保文件使用UTF-8编码

### 日志查看

服务运行时会输出详细日志，包括：
- 验证进度
- API调用状态
- 错误信息和建议

## 开发和扩展

项目结构：
```
mcp-paper-verification/
├── src/mcp_paper_verification/
│   ├── __init__.py
│   ├── server.py          # MCP服务器
│   └── verifier.py        # 验证逻辑
├── tests/                 # 测试文件
├── pyproject.toml        # 项目配置
└── README.md
```

### 添加新的验证功能

1. 在`verifier.py`中的`PaperVerifier`类中添加新方法
2. 在`server.py`中添加对应的MCP工具
3. 更新`generate_report`函数以包含新检查项

## 许可证

MIT License

## 贡献

欢迎提交问题报告和功能请求！ 