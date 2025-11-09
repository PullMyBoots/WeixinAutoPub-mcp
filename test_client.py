#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 WeChat Pub MCP 客户端
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp_server import WeChatPubMCPServer
import asyncio

async def test():
    """测试发布功能"""
    server = WeChatPubMCPServer()
    
    # 测试参数
    test_doc = project_root / "daily_report" / "2025-11-08.md"
    
    if not test_doc.exists():
        print(f"测试文档不存在: {test_doc}")
        return
    
    arguments = {
        "document_path": str(test_doc)
    }
    
    print("开始测试发布功能...")
    print(f"文档路径: {test_doc}")
    print()
    
    result = await server._handle_publish_to_wechat(arguments)
    
    for content in result:
        print(content.text)

if __name__ == "__main__":
    asyncio.run(test())

