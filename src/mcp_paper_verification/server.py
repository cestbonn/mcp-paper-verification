"""
MCP Paper Verification 服务
提供综合的学术论文验证功能
"""

import logging
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP, Context
from mcp_paper_verification.verifier import verify_paper, generate_report
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 创建MCP服务器
mcp = FastMCP(
    "PaperVerificationServer",
    dependencies=["bibtexparser", "httpx"],
    verbose=True,
    debug=True,
)


@mcp.tool()
async def verify_paper_comprehensive(
    ctx: Context,
    md_file_path: str,
    bib_file_path: Optional[str] = None,
    serper_api_key: Optional[str] = None,
    generate_markdown_report: bool = True
) -> Dict[str, Any]:
    """
    综合验证学术论文的格式和内容
    
    Args:
        md_file_path: Markdown格式论文文件的路径
        bib_file_path: BibTeX参考文献文件的路径（可选）
        serper_api_key: Serper API密钥，用于验证参考文献真实性（可选，会自动从环境变量获取）
        generate_markdown_report: 是否生成Markdown格式的详细报告
    
    Returns:
        Dict: 包含验证结果和详细报告的字典
    """
    
    try:
        logger.info(f"开始验证论文: {md_file_path}")
        
        # 如果没有提供API密钥，尝试从环境变量获取
        if not serper_api_key:
            serper_api_key = os.getenv('SERPER_API_KEY')
        
        # 执行综合验证
        verification_results = await verify_paper(
            md_file_path=md_file_path,
            bib_file_path=bib_file_path,
            serper_api_key=serper_api_key
        )
        
        if not verification_results["success"]:
            return {
                "status": "error",
                "error": verification_results["error"],
                "md_file_path": md_file_path
            }
        
        # 添加时间戳
        verification_results["timestamp"] = datetime.now().isoformat()
        
        # 生成报告
        report = ""
        if generate_markdown_report:
            report = generate_report(verification_results)
        
        # 统计问题总数
        results = verification_results["verification_results"]
        total_issues = sum(1 for result in results.values() if result.get("has_issues", False))
        
        return {
            "status": "success",
            "md_file_path": md_file_path,
            "bib_file_path": bib_file_path,
            "total_issues_found": total_issues,
            "verification_summary": {
                "sparse_content": results["sparse_content"]["has_issues"],
                "stereotype_content": results["stereotype_content"]["has_issues"],
                "latex_formulas": results["latex_formulas"]["has_issues"],
                "citations": results["citations"]["has_issues"],
                "reference_count": results["reference_count"]["has_issues"],
                "images": results["images"]["has_issues"],
                "code_blocks": results["code_blocks"]["has_issues"],
                "bib_references": results.get("bib_references", {}).get("has_issues", False)
            },
            "detailed_results": verification_results,
            "markdown_report": report
        }
        
    except Exception as e:
        logger.error(f"验证过程中出错: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": f"验证过程中出错: {str(e)}",
            "md_file_path": md_file_path
        }


@mcp.tool()
async def verify_sparse_content_only(
    ctx: Context,
    md_file_path: str
) -> Dict[str, Any]:
    """
    仅验证论文的罗列情况（稀疏内容检查）
    
    Args:
        md_file_path: Markdown格式论文文件的路径
    
    Returns:
        Dict: 罗列情况验证结果
    """
    
    try:
        if not os.path.exists(md_file_path):
            return {
                "status": "error",
                "error": f"文件不存在: {md_file_path}"
            }
        
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        from mcp_paper_verification.verifier import PaperVerifier
        verifier = PaperVerifier()
        result = verifier.verify_sparse_content(content)
        
        return {
            "status": "success",
            "md_file_path": md_file_path,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"稀疏内容验证失败: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "md_file_path": md_file_path
        }


@mcp.tool()
async def verify_stereotype_content_only(
    ctx: Context,
    md_file_path: str
) -> Dict[str, Any]:
    """
    仅验证论文的刻板印象情况
    
    Args:
        md_file_path: Markdown格式论文文件的路径
    
    Returns:
        Dict: 刻板印象验证结果
    """
    
    try:
        if not os.path.exists(md_file_path):
            return {
                "status": "error",
                "error": f"文件不存在: {md_file_path}"
            }
        
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        from mcp_paper_verification.verifier import PaperVerifier
        verifier = PaperVerifier()
        result = verifier.verify_stereotype_content(content)
        
        return {
            "status": "success",
            "md_file_path": md_file_path,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"刻板印象验证失败: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "md_file_path": md_file_path
        }


@mcp.tool()
async def verify_bib_references_only(
    ctx: Context,
    bib_file_path: str,
    serper_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    仅验证BibTeX文件中参考文献的真实性
    
    Args:
        bib_file_path: BibTeX文件路径
        serper_api_key: Serper API密钥（可选，会自动从环境变量获取）
    
    Returns:
        Dict: 参考文献验证结果
    """
    
    try:
        if not serper_api_key:
            serper_api_key = os.getenv('SERPER_API_KEY')
        
        from mcp_paper_verification.verifier import PaperVerifier
        verifier = PaperVerifier(serper_api_key)
        result = verifier.verify_bib_references(bib_file_path)
        
        return {
            "status": "success",
            "bib_file_path": bib_file_path,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"参考文献验证失败: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "bib_file_path": bib_file_path
        }


@mcp.tool()
async def verify_reference_count_only(
    ctx: Context,
    md_file_path: str,
    min_references: int = 15
) -> Dict[str, Any]:
    """
    仅验证论文的引用数量统计
    
    Args:
        md_file_path: Markdown格式论文文件的路径
        min_references: 建议的最少引用数量（默认15）
    
    Returns:
        Dict: 引用数量验证结果
    """
    
    try:
        if not os.path.exists(md_file_path):
            return {
                "status": "error",
                "error": f"文件不存在: {md_file_path}"
            }
        
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        from mcp_paper_verification.verifier import PaperVerifier
        verifier = PaperVerifier()
        result = verifier.verify_reference_count(content, min_references)
        
        return {
            "status": "success",
            "md_file_path": md_file_path,
            "min_references_setting": min_references,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"引用数量验证失败: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "md_file_path": md_file_path
        }


@mcp.tool()
async def health_check(ctx: Context) -> str:
    """
    健康检查端点，用于验证服务是否正常运行
    
    Returns:
        str: 服务状态信息
    """
    serper_key = os.getenv('SERPER_API_KEY')
    serper_status = "✅ 已配置" if serper_key else "❌ 未配置"
    
    return f"MCP Paper Verification服务运行正常\nSerper API密钥状态: {serper_status}"


def cli_main():
    """CLI入口点"""
    logger.info("MCP Paper Verification STDIO服务准备启动...")
    
    # 检查Serper API密钥
    serper_key = os.getenv('SERPER_API_KEY')
    if not serper_key:
        logger.warning("警告: 未找到SERPER_API_KEY环境变量，参考文献验证功能将不可用")
    else:
        logger.info("Serper API密钥已配置")
    
    logger.info("MCP Paper Verification STDIO服务已启动，等待输入...")
    
    # 启动服务器
    mcp.run()


def main():
    """主函数"""
    cli_main()


if __name__ == "__main__":
    main() 