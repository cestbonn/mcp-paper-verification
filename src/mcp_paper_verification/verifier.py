"""
综合论文验证器
包含多种验证功能：罗列检查、刻板印象检查、格式检查、引用检查等
"""

import os
import re
import json
import statistics
import http.client
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import bibtexparser


class WebSearchAPI:
    """Google Serper API客户端"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('SERPER_API_KEY')
        self.base_url = "google.serper.dev"
        
    def search_reference(self, title: str, authors: str = "") -> Dict[str, Any]:
        """搜索参考文献是否真实存在"""
        if not self.api_key:
            return {
                "success": False,
                "error": "SERPER_API_KEY not provided"
            }
        
        # 构建搜索查询
        query = f'"{title}"'
        if authors:
            query += f' {authors}'
        
        payload = {
            "q": query,
            "num": 3
        }
        
        try:
            conn = http.client.HTTPSConnection(self.base_url)
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            conn.request("POST", "/search", json.dumps(payload), headers)
            response = conn.getresponse()
            data = response.read()
            
            if response.status != 200:
                return {
                    "success": False,
                    "error": f"API request failed with status {response.status}"
                }
            
            result = json.loads(data.decode("utf-8"))
            
            # 检查是否找到相关结果
            if "organic" in result and len(result["organic"]) > 0:
                return {
                    "success": True,
                    "found": True,
                    "results": result["organic"][:3]
                }
            else:
                return {
                    "success": True,
                    "found": False,
                    "results": []
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Search request failed: {str(e)}"
            }
        finally:
            if 'conn' in locals():
                conn.close()


class PaperVerifier:
    """综合论文验证器"""
    
    def __init__(self, serper_api_key: Optional[str] = None):
        self.web_search = WebSearchAPI(serper_api_key)
    
    def verify_sparse_content(self, content: str) -> Dict[str, Any]:
        """检查罗列情况（基于sparse_verifier.py）"""
        
        # 基本统计
        total_chars = len(content)
        total_chars_no_spaces = len(content.replace(' ', '').replace('\t', '').replace('\n', ''))
        
        # 分割段落
        paragraphs = []
        sections = re.split(r'\n\s*\n', content.strip())
        
        for section in sections:
            if section.strip():
                lines = section.split('\n')
                current_para = []
                
                for line in lines:
                    line = line.strip()
                    if line:
                        # 跳过markdown标题行
                        if re.match(r'^#{1,6}\s+', line):
                            if current_para:
                                paragraphs.append('\n'.join(current_para))
                                current_para = []
                            continue
                        current_para.append(line)
                    elif current_para:
                        paragraphs.append('\n'.join(current_para))
                        current_para = []
                
                if current_para:
                    paragraphs.append('\n'.join(current_para))
        
        # 过滤空段落和过短段落
        paragraphs = [p.strip() for p in paragraphs if p.strip() and len(p.strip()) > 20]
        
        if not paragraphs:
            return {
                "has_issues": True,
                "issues": ["No meaningful paragraphs found"],
                "sparsity_score": 1.0
            }
        
        # 计算段落长度统计
        paragraph_lengths = [len(p) for p in paragraphs]
        median_length = statistics.median(paragraph_lengths)
        mean_length = statistics.mean(paragraph_lengths)
        
        issues = []
        sparsity_score = 0.0
        
        # 1. 短段落比例检查
        short_paragraphs = [p for p in paragraph_lengths if p < 300]
        short_para_ratio = len(short_paragraphs) / len(paragraph_lengths)
        if short_para_ratio > 0.6:
            issues.append(f"过多短段落 ({short_para_ratio:.1%} 的段落少于300字符)")
            sparsity_score += 0.3
        
        # 2. 极短段落比例检查
        very_short_paragraphs = [p for p in paragraph_lengths if p < 100]
        very_short_ratio = len(very_short_paragraphs) / len(paragraph_lengths)
        if very_short_ratio > 0.4:
            issues.append(f"过多极短段落 ({very_short_ratio:.1%} 的段落少于100字符)")
            sparsity_score += 0.2
        
        # 3. 检测列表标记模式
        list_patterns = [
            r'^\s*\d+[\.\)]\s*',  # 数字列表
            r'^\s*[a-zA-Z][\.\)]\s*',  # 字母列表
            r'^\s*[-\*\+•]\s*',  # 符号列表
            r'^\s*[第]\d+[章节条]\s*',  # 中文章节标记
            r'^\s*[一二三四五六七八九十]+[\.\、]\s*',  # 中文数字列表
        ]
        
        list_like_paragraphs = 0
        for para in paragraphs:
            for pattern in list_patterns:
                if re.search(pattern, para, re.MULTILINE):
                    list_like_paragraphs += 1
                    break
        
        list_ratio = list_like_paragraphs / len(paragraphs)
        if list_ratio > 0.3:
            issues.append(f"过多列表式段落 ({list_ratio:.1%} 的段落为列表格式)")
            sparsity_score += 0.2
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "sparsity_score": sparsity_score,
            "paragraph_count": len(paragraphs),
            "median_length": median_length
        }
    
    def verify_stereotype_content(self, content: str) -> Dict[str, Any]:
        """检查刻板印象情况（基于stereotype_verifier.py）"""
        
        # 定义刻板印象词
        stereotype_words = [
            "首先，", "其次，", "再次，", "最后，", "再者，",
            "综上所述，", "值得注意的是，", "总而言之，", "换句话说，",
            "毫无疑问，", "显而易见，", "众所周知，"
        ]
        
        # 分割段落
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        issues = []
        found_stereotype_words = []
        paragraphs_with_stereotype = 0
        
        for paragraph in paragraphs:
            has_stereotype = False
            
            # 检测固定的刻板印象词
            for word in stereotype_words:
                if word in paragraph:
                    if not has_stereotype:
                        paragraphs_with_stereotype += 1
                        has_stereotype = True
                    if word not in found_stereotype_words:
                        found_stereotype_words.append(word)
            
            # 检测各种加粗标题模式
            bold_patterns = [
                (r'^\*\*(.{1,15})\*\*[：:]', "段落以加粗短语和冒号开头"),
                (r'\d+\.\s*\*\*(.{1,15})\*\*[：:]', "数字序号+加粗标题"),
                (r'^\s*-\s*\*\*(.{1,15})\*\*[：:]', "列表项+加粗标题")
            ]
            
            for pattern, description in bold_patterns:
                if re.match(pattern, paragraph):
                    if not has_stereotype:
                        paragraphs_with_stereotype += 1
                        has_stereotype = True
                    if description not in found_stereotype_words:
                        found_stereotype_words.append(description)
                    break
        
        if found_stereotype_words:
            issues.append(f"发现刻板印象表达: {', '.join(found_stereotype_words)}")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "found_expressions": found_stereotype_words,
            "affected_paragraphs": paragraphs_with_stereotype,
            "total_paragraphs": len(paragraphs)
        }
    
    def verify_latex_formulas(self, content: str) -> Dict[str, Any]:
        """检查LaTeX公式格式"""
        
        issues = []
        
        # 检查裸露的希腊字母
        greek_letters = [
            'α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω',
            'Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ', 'Ι', 'Κ', 'Λ', 'Μ', 'Ν', 'Ξ', 'Ο', 'Π', 'Ρ', 'Σ', 'Τ', 'Υ', 'Φ', 'Χ', 'Ψ', 'Ω'
        ]
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # 跳过已经在LaTeX块中的内容
            if '$' in line or '$$' in line:
                continue
            
            # 排除图片引用的内容（包括alt text）
            # 移除图片语法 ![alt text](url)
            line_without_images = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', line)
                
            for letter in greek_letters:
                if letter in line_without_images:
                    issues.append(f"第{i}行：发现裸露的希腊字母 '{letter}'，应使用LaTeX格式")
        
        # 检查常见数学符号
        math_symbols = ['∑', '∏', '∫', '∞', '≤', '≥', '≠', '±', '∝', '∈', '∀', '∃']
        for i, line in enumerate(lines, 1):
            if '$' in line or '$$' in line:
                continue
            
            # 排除图片引用的内容
            line_without_images = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', line)
                
            for symbol in math_symbols:
                if symbol in line_without_images:
                    issues.append(f"第{i}行：发现裸露的数学符号 '{symbol}'，应使用LaTeX格式")
        
        # 检查是否有数学表达式没有用LaTeX包围
        math_patterns = [
            r'\b[a-zA-Z]\s*=\s*[a-zA-Z0-9+\-*/^()]+',  # 变量赋值
            r'\b[a-zA-Z]+\s*\^\s*[0-9]+',  # 幂运算
            r'\b[a-zA-Z]+_[a-zA-Z0-9]+',  # 下标
        ]
        
        for i, line in enumerate(lines, 1):
            if '$' in line or '$$' in line:
                continue
            
            # 排除图片引用的内容
            line_without_images = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', line)
                
            for pattern in math_patterns:
                if re.search(pattern, line_without_images):
                    issues.append(f"第{i}行：发现可能的数学表达式，建议使用LaTeX格式包围")
                    break
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues
        }
    
    def verify_citations(self, content: str, bib_file_path: Optional[str] = None) -> Dict[str, Any]:
        """检查文献引用格式和存在性"""
        
        issues = []
        
        # 查找所有引用
        citation_pattern = r'\[@([^\]]+)\]'
        citations = re.findall(citation_pattern, content)
        
        if not citations:
            return {
                "has_issues": False,
                "issues": [],
                "citations_found": 0,
                "unique_citations": 0
            }
        
        # 检查引用格式，先移除图片引用再检查
        content_without_images = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', content)
        invalid_citation_pattern = r'\[(?!@)[^\]]*\]'
        invalid_citations = re.findall(invalid_citation_pattern, content_without_images)
        
        for invalid in invalid_citations:
            # 排除正常的链接和数字引用
            if not ('http' in invalid or invalid.isdigit()):
                issues.append(f"发现非标准引用格式: [{invalid}]，应使用[@key]格式")
        
        # 如果提供了bib文件，检查引用是否存在
        if bib_file_path and os.path.exists(bib_file_path):
            try:
                with open(bib_file_path, 'r', encoding='utf-8') as f:
                    bib_content = f.read()
                
                # 使用旧版本API
                bib_db = bibtexparser.loads(bib_content)
                bib_keys = set(bib_db.entries_dict.keys())
                
                for citation in citations:
                    if citation not in bib_keys:
                        issues.append(f"引用 [@{citation}] 在bib文件中不存在")
                        
            except Exception as e:
                issues.append(f"读取bib文件时出错: {str(e)}")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "citations_found": len(citations),
            "unique_citations": len(set(citations))
        }
    
    def verify_images(self, content: str, md_file_path: str) -> Dict[str, Any]:
        """检查图片链接和文件存在性"""
        
        issues = []
        
        # 查找所有图片引用
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        images = re.findall(image_pattern, content)
        
        md_dir = Path(md_file_path).parent
        
        for alt_text, img_path in images:
            # 检查是否为相对路径
            if img_path.startswith('http://') or img_path.startswith('https://'):
                issues.append(f"图片 '{alt_text}' 使用了网络链接，应使用本地绝对路径: {img_path}")
                continue
            
            # 检查是否为绝对路径
            if not os.path.isabs(img_path):
                issues.append(f"图片 '{alt_text}' 使用了相对路径，应使用绝对路径: {img_path}")
                continue
            
            # 检查文件是否存在
            if not os.path.exists(img_path):
                issues.append(f"图片文件不存在: {img_path}")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "images_found": len(images)
        }
    
    def verify_code_blocks(self, content: str) -> Dict[str, Any]:
        """检查代码块（不允许存在）"""
        
        issues = []
        
        # 检查代码块
        code_block_patterns = [
            (r'```[\s\S]*?```', "代码块"),
            (r'`[^`\n]+`', "行内代码"),
            (r'^\s{4,}[^\s]', "缩进代码块"),
        ]
        
        lines = content.split('\n')
        
        # 检查围栏代码块
        in_code_block = False
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    block_type = line.strip()[3:].strip() or "代码"
                    issues.append(f"第{i}行：发现{block_type}代码块，论文中不应包含代码块")
                else:
                    in_code_block = False
        
        # 检查行内代码
        for i, line in enumerate(lines, 1):
            if '`' in line and not line.strip().startswith('```'):
                # 简单检查是否为行内代码
                backtick_count = line.count('`')
                if backtick_count >= 2:
                    issues.append(f"第{i}行：发现行内代码，论文中不应包含代码")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues
        }
    
    def verify_bib_references(self, bib_file_path: str) -> Dict[str, Any]:
        """验证bib文件中的参考文献真实性"""
        
        if not os.path.exists(bib_file_path):
            return {
                "has_issues": True,
                "issues": [f"bib文件不存在: {bib_file_path}"],
                "verified_count": 0,
                "total_count": 0
            }
        
        issues = []
        verified_count = 0
        total_count = 0
        
        try:
            with open(bib_file_path, 'r', encoding='utf-8') as f:
                bib_content = f.read()
            
            # 使用旧版本API
            bib_db = bibtexparser.loads(bib_content)
            entries = bib_db.entries
            
            for entry in entries:
                total_count += 1
                
                title = entry.get('title', '')
                author = entry.get('author', '')
                entry_key = entry.get('ID', '')
                
                if not title:
                    issues.append(f"参考文献 {entry_key} 缺少标题")
                    continue
                
                # 搜索验证
                search_result = self.web_search.search_reference(title, author)
                
                if not search_result["success"]:
                    issues.append(f"参考文献 {entry_key} 验证失败: {search_result.get('error', 'Unknown error')}")
                elif not search_result["found"]:
                    issues.append(f"参考文献 {entry_key} 可能不真实存在: {title}")
                else:
                    verified_count += 1
                    
        except Exception as e:
            issues.append(f"解析bib文件时出错: {str(e)}")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "verified_count": verified_count,
            "total_count": total_count
        }


async def verify_paper(md_file_path: str, bib_file_path: Optional[str] = None, 
                      serper_api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    综合验证论文
    
    Args:
        md_file_path: Markdown文件路径
        bib_file_path: bib文件路径（可选）
        serper_api_key: Serper API密钥（可选）
    
    Returns:
        验证报告
    """
    
    # 检查文件是否存在
    if not os.path.exists(md_file_path):
        return {
            "success": False,
            "error": f"Markdown文件不存在: {md_file_path}"
        }
    
    # 读取文件内容
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {
            "success": False,
            "error": f"读取文件失败: {str(e)}"
        }
    
    verifier = PaperVerifier(serper_api_key)
    
    # 执行各项验证
    results = {
        "success": True,
        "md_file_path": md_file_path,
        "bib_file_path": bib_file_path,
        "verification_results": {
            "sparse_content": verifier.verify_sparse_content(content),
            "stereotype_content": verifier.verify_stereotype_content(content),
            "latex_formulas": verifier.verify_latex_formulas(content),
            "citations": verifier.verify_citations(content, bib_file_path),
            "images": verifier.verify_images(content, md_file_path),
            "code_blocks": verifier.verify_code_blocks(content),
        }
    }
    
    # 如果提供了bib文件，验证参考文献
    if bib_file_path:
        results["verification_results"]["bib_references"] = verifier.verify_bib_references(bib_file_path)
    
    return results


def generate_report(verification_results: Dict[str, Any]) -> str:
    """生成详细的验证报告（Markdown格式）"""
    
    if not verification_results["success"]:
        return f"# 论文验证报告\n\n**错误**: {verification_results['error']}\n"
    
    md_file = verification_results["md_file_path"]
    bib_file = verification_results.get("bib_file_path", "未提供")
    
    report = f"""# 论文验证报告

**文件路径**: {md_file}
**bib文件**: {bib_file}
**验证时间**: {verification_results.get('timestamp', 'N/A')}

---

"""
    
    results = verification_results["verification_results"]
    
    # 1. 罗列情况检查
    sparse = results["sparse_content"]
    report += "## 1. 罗列情况检查\n\n"
    if sparse["has_issues"]:
        report += "**状态**: ❌ 发现问题\n\n"
        for issue in sparse["issues"]:
            report += f"- {issue}\n"
        report += f"\n**稀疏度得分**: {sparse['sparsity_score']:.2f}\n"
    else:
        report += "**状态**: ✅ 通过\n"
    report += f"**段落数量**: {sparse['paragraph_count']}\n\n"
    
    # 2. 刻板印象检查
    stereotype = results["stereotype_content"]
    report += "## 2. 刻板印象检查\n\n"
    if stereotype["has_issues"]:
        report += "**状态**: ❌ 发现问题\n\n"
        for issue in stereotype["issues"]:
            report += f"- {issue}\n"
        report += f"\n**受影响段落**: {stereotype['affected_paragraphs']}/{stereotype['total_paragraphs']}\n"
    else:
        report += "**状态**: ✅ 通过\n"
    report += "\n"
    
    # 3. LaTeX公式检查
    latex = results["latex_formulas"]
    report += "## 3. LaTeX公式格式检查\n\n"
    if latex["has_issues"]:
        report += "**状态**: ❌ 发现问题\n\n"
        for issue in latex["issues"]:
            report += f"- {issue}\n"
    else:
        report += "**状态**: ✅ 通过\n"
    report += "\n"
    
    # 4. 文献引用检查
    citations = results["citations"]
    report += "## 4. 文献引用检查\n\n"
    if citations["has_issues"]:
        report += "**状态**: ❌ 发现问题\n\n"
        for issue in citations["issues"]:
            report += f"- {issue}\n"
    else:
        report += "**状态**: ✅ 通过\n"
    report += f"**引用数量**: {citations['citations_found']} (唯一: {citations['unique_citations']})\n\n"
    
    # 5. 图片检查
    images = results["images"]
    report += "## 5. 图片链接检查\n\n"
    if images["has_issues"]:
        report += "**状态**: ❌ 发现问题\n\n"
        for issue in images["issues"]:
            report += f"- {issue}\n"
    else:
        report += "**状态**: ✅ 通过\n"
    report += f"**图片数量**: {images['images_found']}\n\n"
    
    # 6. 代码块检查
    code_blocks = results["code_blocks"]
    report += "## 6. 代码块检查\n\n"
    if code_blocks["has_issues"]:
        report += "**状态**: ❌ 发现问题\n\n"
        for issue in code_blocks["issues"]:
            report += f"- {issue}\n"
    else:
        report += "**状态**: ✅ 通过\n"
    report += "\n"
    
    # 7. bib文件验证
    if "bib_references" in results:
        bib_refs = results["bib_references"]
        report += "## 7. bib文件参考文献验证\n\n"
        if bib_refs["has_issues"]:
            report += "**状态**: ❌ 发现问题\n\n"
            for issue in bib_refs["issues"]:
                report += f"- {issue}\n"
        else:
            report += "**状态**: ✅ 通过\n"
        report += f"**验证成功**: {bib_refs['verified_count']}/{bib_refs['total_count']}\n\n"
    
    # 总结
    all_results = [results[key] for key in results]
    total_issues = sum(1 for result in all_results if result.get("has_issues", False))
    
    report += "---\n\n## 总结\n\n"
    if total_issues > 0:
        report += f"**总体状态**: ❌ 发现 {total_issues} 类问题\n\n"
        report += "**建议**: 请根据上述问题逐一修正论文内容。\n"
    else:
        report += "**总体状态**: ✅ 所有检查通过\n\n"
        report += "**结论**: 论文格式和内容符合要求。\n"
    
    return report 