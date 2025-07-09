#!/usr/bin/env python3
"""
MCP Paper Verification 服务测试脚本
"""

import asyncio
import json
import os
import tempfile
import argparse
from pathlib import Path
import sys

# 添加项目路径到sys.path
project_root = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(project_root))

from mcp_paper_verification.verifier import verify_paper, generate_report


def create_test_files():
    """创建测试用的文件"""
    
    # 创建有问题的markdown文件
    problematic_md = """# 测试论文

## 摘要

首先，我们提出了一个新方法。其次，我们验证了这个方法。最后，我们得出了结论。

## 介绍

这是一个很短的段落。

这是另一个很短的段落。

下面是一些α和β字符，还有一些数学表达式 x = y + 1，这些都没有用LaTeX包围。

## 方法

**方法一**：这是第一个方法。

**方法二**：这是第二个方法。

下面包含一些代码：

```python
def hello():
    print("Hello, World!")
```

还有一些引用 [1] 和 [@nonexistent]。

图片引用：![test](relative/path/image.png)

网络图片：![web](https://example.com/image.png)

## 结果

1. 结果一
2. 结果二
3. 结果三

## 结论

综上所述，我们的方法很好。值得注意的是，它有很多优点。
"""

    # 创建bib文件
    bib_content = """@article{example2023,
  title={A Non-existent Paper for Testing},
  author={Test Author},
  journal={Test Journal},
  year={2023}
}

@inproceedings{real2020,
  title={Attention Is All You Need},
  author={Vaswani, Ashish and Shazeer, Noam and Parmar, Niki},
  booktitle={Advances in Neural Information Processing Systems},
  year={2017}
}
"""

    # 创建临时文件
    md_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8')
    md_file.write(problematic_md)
    md_file.close()
    
    bib_file = tempfile.NamedTemporaryFile(mode='w', suffix='.bib', delete=False, encoding='utf-8')
    bib_file.write(bib_content)
    bib_file.close()
    
    return md_file.name, bib_file.name


async def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    
    try:
        from mcp_paper_verification.server import health_check
        from mcp.server.fastmcp import Context
        
        # 创建模拟上下文
        ctx = Context()
        
        result = await health_check(ctx)
        print(f"✅ 健康检查通过: {result}")
        return True
    except Exception as e:
        print(f"❌ 健康检查失败: {str(e)}")
        return False


async def test_comprehensive_verification(md_file_path, bib_file_path):
    """测试综合验证功能"""
    print("🔍 测试综合验证功能...")
    
    try:
        from mcp_paper_verification.server import verify_paper_comprehensive
        from mcp.server.fastmcp import Context
        
        ctx = Context()
        
        result = await verify_paper_comprehensive(
            ctx=ctx,
            md_file_path=md_file_path,
            bib_file_path=bib_file_path,
            generate_markdown_report=True
        )
        
        print(f"✅ 综合验证完成")
        print(f"📊 总问题数: {result.get('total_issues_found', 'N/A')}")
        
        # 显示验证摘要
        summary = result.get('verification_summary', {})
        print("\n📋 验证摘要:")
        for check, has_issues in summary.items():
            status = "❌" if has_issues else "✅"
            print(f"  {status} {check}")
        
        # 保存报告到文件
        if result.get('markdown_report'):
            report_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8')
            report_file.write(result['markdown_report'])
            report_file.close()
            print(f"\n📄 详细报告已保存到: {report_file.name}")
        
        return True
    except Exception as e:
        print(f"❌ 综合验证失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_individual_checks(md_file_path, bib_file_path):
    """测试各个单独的检查功能"""
    print("🔍 测试各个单独检查功能...")
    
    try:
        from mcp_paper_verification.server import (
            verify_sparse_content_only,
            verify_stereotype_content_only,
            verify_bib_references_only
        )
        from mcp.server.fastmcp import Context
        
        ctx = Context()
        
        # 测试罗列检查
        print("\n  📝 测试罗列内容检查...")
        sparse_result = await verify_sparse_content_only(ctx, md_file_path)
        if sparse_result['status'] == 'success':
            print(f"    ✅ 罗列检查完成，有问题: {sparse_result['result']['has_issues']}")
        else:
            print(f"    ❌ 罗列检查失败: {sparse_result['error']}")
        
        # 测试刻板印象检查
        print("\n  🎭 测试刻板印象检查...")
        stereotype_result = await verify_stereotype_content_only(ctx, md_file_path)
        if stereotype_result['status'] == 'success':
            print(f"    ✅ 刻板印象检查完成，有问题: {stereotype_result['result']['has_issues']}")
        else:
            print(f"    ❌ 刻板印象检查失败: {stereotype_result['error']}")
        
        # 测试参考文献检查（如果有Serper API密钥）
        if os.getenv('SERPER_API_KEY'):
            print("\n  📚 测试参考文献验证...")
            bib_result = await verify_bib_references_only(ctx, bib_file_path)
            if bib_result['status'] == 'success':
                print(f"    ✅ 参考文献验证完成，有问题: {bib_result['result']['has_issues']}")
            else:
                print(f"    ❌ 参考文献验证失败: {bib_result['error']}")
        else:
            print("\n  📚 跳过参考文献验证（未配置SERPER_API_KEY）")
        
        return True
    except Exception as e:
        print(f"❌ 单独检查测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_direct_verification(md_file_path, bib_file_path):
    """测试直接调用验证函数"""
    print("🔍 测试直接验证功能...")
    
    try:
        result = await verify_paper(
            md_file_path=md_file_path,
            bib_file_path=bib_file_path,
            serper_api_key=os.getenv('SERPER_API_KEY')
        )
        
        if result['success']:
            print("✅ 直接验证完成")
            
            # 生成报告
            report = generate_report(result)
            print(f"📊 报告长度: {len(report)} 字符")
            
            # 保存到文件
            report_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8')
            report_file.write(report)
            report_file.close()
            print(f"📄 报告已保存到: {report_file.name}")
            
            return True
        else:
            print(f"❌ 直接验证失败: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ 直接验证异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_files(*file_paths):
    """清理临时文件"""
    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"⚠️ 清理文件失败 {file_path}: {str(e)}")


async def main():
    """主测试函数"""
    parser = argparse.ArgumentParser(description='测试MCP Paper Verification服务')
    parser.add_argument('--test', choices=['health', 'comprehensive', 'individual', 'direct', 'all'],
                       default='all', help='选择要运行的测试')
    parser.add_argument('--md-file', help='使用指定的MD文件进行测试')
    parser.add_argument('--bib-file', help='使用指定的BIB文件进行测试')
    
    args = parser.parse_args()
    
    print("🚀 MCP Paper Verification 服务测试开始\n")
    
    # 检查环境
    serper_key = os.getenv('SERPER_API_KEY')
    if serper_key:
        print(f"🔑 Serper API密钥: 已配置 ({serper_key[:10]}...)")
    else:
        print("⚠️ Serper API密钥: 未配置（参考文献验证将跳过）")
    
    # 准备测试文件
    if args.md_file and args.bib_file:
        md_file_path = args.md_file
        bib_file_path = args.bib_file
        cleanup_files_at_end = False
    else:
        print("\n📁 创建测试文件...")
        md_file_path, bib_file_path = create_test_files()
        print(f"  MD文件: {md_file_path}")
        print(f"  BIB文件: {bib_file_path}")
        cleanup_files_at_end = True
    
    # 运行测试
    test_results = []
    
    try:
        if args.test in ['health', 'all']:
            print("\n" + "="*50)
            result = await test_health_check()
            test_results.append(('健康检查', result))
        
        if args.test in ['comprehensive', 'all']:
            print("\n" + "="*50)
            result = await test_comprehensive_verification(md_file_path, bib_file_path)
            test_results.append(('综合验证', result))
        
        if args.test in ['individual', 'all']:
            print("\n" + "="*50)
            result = await test_individual_checks(md_file_path, bib_file_path)
            test_results.append(('单独检查', result))
        
        if args.test in ['direct', 'all']:
            print("\n" + "="*50)
            result = await test_direct_verification(md_file_path, bib_file_path)
            test_results.append(('直接验证', result))
    
    finally:
        # 清理临时文件
        if cleanup_files_at_end:
            print("\n🧹 清理临时文件...")
            cleanup_files(md_file_path, bib_file_path)
    
    # 输出测试结果
    print("\n" + "="*50)
    print("📋 测试结果汇总:")
    all_passed = True
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！MCP Paper Verification服务工作正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 