# MCP Paper Verification

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Protocol-green.svg)](https://modelcontextprotocol.io/)

A comprehensive academic paper verification MCP server that analyzes Markdown-formatted papers for various quality and formatting issues.

## 🔍 Features

### Verification Components

1. **Sparse Content Detection**
   - Analyzes paragraph length and content density
   - Identifies list-like content patterns
   - Calculates sparsity scores to detect low-quality content

2. **Stereotype Expression Detection**
   - Detects common academic template phrases (e.g., "First,", "Second,", "Finally,")
   - Identifies overused bold title patterns
   - Analyzes expression diversity

3. **LaTeX Formula Validation**
   - Detects naked Greek letters and mathematical symbols
   - Ensures proper LaTeX formatting for mathematical expressions
   - Validates Markdown-compatible formula syntax

4. **Citation Format Verification**
   - Validates citation format (should be `[@key]`)
   - Cross-references citations with BibTeX files
   - Reports missing or invalid references

5. **Image Link Validation**
   - Ensures use of absolute paths instead of relative or web links
   - Verifies image file existence
   - Validates image reference format

6. **Code Block Detection**
   - Detects and reports any code blocks (inappropriate for academic papers)
   - Includes fenced code blocks, inline code, and indented code blocks

7. **Reference Authenticity Verification**
   - Uses Google Serper API to verify reference authenticity
   - Validates BibTeX file format and completeness
   - Provides verification statistics

## 🚀 Installation

### Prerequisites

- Python 3.10+
- Valid Serper API key (for reference verification)

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mcp-paper-verification
   ```

2. Install dependencies using uv:
   ```bash
   uv install
   ```

3. Set up environment variables:
   ```bash
   export SERPER_API_KEY="your_serper_api_key_here"
   ```

   Or create a `.env` file:
   ```
   SERPER_API_KEY=your_serper_api_key_here
   ```

## 📖 Usage

### As MCP Server

Start the MCP server:
```bash
uv run mcp-paper-verification
```

### MCP Client Configuration

#### Claude Desktop

Add to `~/.config/claude-desktop/claude_desktop_config.json`:

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

#### Cherry Studio

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

### Available Tools

#### 1. `verify_paper_comprehensive`
Performs comprehensive verification of all aspects:
- **Parameters**:
  - `md_file_path`: Path to Markdown paper file
  - `bib_file_path`: Path to BibTeX file (optional)
  - `serper_api_key`: Serper API key (optional)
  - `generate_markdown_report`: Generate Markdown report (default: true)

#### 2. `verify_sparse_content_only`
Check content sparsity only:
- **Parameters**:
  - `md_file_path`: Path to Markdown paper file

#### 3. `verify_stereotype_content_only`
Check stereotype expressions only:
- **Parameters**:
  - `md_file_path`: Path to Markdown paper file

#### 4. `verify_bib_references_only`
Verify reference authenticity only:
- **Parameters**:
  - `bib_file_path`: Path to BibTeX file
  - `serper_api_key`: Serper API key (optional)

#### 5. `health_check`
Service health check

## 💡 Example Usage

### In MCP Client

```
Verify this paper: /path/to/paper.md with bibliography: /path/to/references.bib
```

### Sample Output

The verification returns:

1. **Verification Summary**: Pass/fail status for each check
2. **Detailed Results**: Specific issue lists for each verification
3. **Markdown Report**: Formatted detailed report including:
   - Specific locations and descriptions of issues
   - Suggestions for improvement
   - Statistical information

## 📋 Quality Standards

### High-quality academic papers should have:

✅ **Content Density**: Paragraphs with sufficient length and substance  
✅ **Expression Diversity**: Avoid overuse of template expressions  
✅ **Format Standards**: Mathematical formulas using proper LaTeX syntax  
✅ **Citation Standards**: Use `[@key]` format with entries in bib file  
✅ **Resource Integrity**: Images using absolute paths with existing files  
✅ **Content Purity**: No code blocks or unrelated content  
✅ **Reference Reliability**: Citations to real, verifiable literature  

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
SERPER_API_KEY=your_key uv run python tests/test_mcp_service.py --test all

# Run specific tests
uv run python tests/test_mcp_service.py --test health
uv run python tests/test_mcp_service.py --test comprehensive
```

## 🛠️ Development

### Project Structure

```
mcp-paper-verification/
├── src/mcp_paper_verification/
│   ├── __init__.py
│   ├── server.py          # MCP server
│   └── verifier.py        # Verification logic
├── tests/                 # Test files
├── pyproject.toml        # Project configuration
├── README.md             # Chinese documentation
└── README_EN.md          # English documentation
```

### Adding New Verification Features

1. Add new methods to the `PaperVerifier` class in `verifier.py`
2. Add corresponding MCP tools in `server.py`
3. Update the `generate_report` function to include new checks

## 🔧 Troubleshooting

### Common Issues

1. **Serper API Errors**: Ensure API key is correct and has sufficient quota
2. **File Path Issues**: Use absolute paths to avoid relative path problems
3. **Encoding Issues**: Ensure files use UTF-8 encoding

### Logging

The service outputs detailed logs during operation, including:
- Verification progress
- API call status
- Error messages and suggestions

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
- Uses [Google Serper API](https://serper.dev/) for reference verification
- Inspired by academic writing quality standards

## 📚 Related Projects

- [mcp-scholar](../mcp_scholar) - Academic search and analysis MCP server
- [AutoPaper](../../AcademicAgent) - Automated academic paper generation

---

**Note**: This is part of the AutoPaper project ecosystem for automated academic paper generation and verification. 