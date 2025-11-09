#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Pub MCP Server
基于 Model Context Protocol 的微信公众平台文章发布服务
"""

import asyncio
import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Any, Sequence
import logging

# 导入 MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
    )
except ImportError:
    print("错误: 请先安装 MCP SDK: pip install mcp", file=sys.stderr)
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('wechat_pub_mcp.log'), logging.StreamHandler()]
)
logger = logging.getLogger('wechat-pub-mcp')


class WeChatPubMCPServer:
    """微信发布 MCP 服务器"""
    
    def __init__(self):
        """初始化服务器"""
        self.server = Server("wechat-pub-mcp")
        self.config_path = Path(__file__).parent / "config.txt"
        self.rust_binary_path = None
        self._setup_handlers()
        self._load_config()
        logger.info("WeChat Pub MCP Server 初始化完成")
    
    def _load_config(self):
        """加载配置文件"""
        if not self.config_path.exists():
            logger.warning(f"配置文件不存在: {self.config_path}")
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('AppID:'):
                        self.app_id = line.split(':', 1)[1].strip()
                    elif line.startswith('AppSecret:'):
                        self.app_secret = line.split(':', 1)[1].strip()
            
            if not hasattr(self, 'app_id') or not hasattr(self, 'app_secret'):
                logger.error("配置文件格式错误，需要 AppID 和 AppSecret")
            else:
                logger.info("配置文件加载成功")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
    
    def _find_rust_binary(self):
        """查找 Rust 二进制文件"""
        plugin_dir = Path(__file__).parent
        target_dir = plugin_dir / "target" / "release" / "wechat_client"
        
        if target_dir.exists():
            self.rust_binary_path = target_dir
            return True
        
        # 尝试 debug 版本
        target_dir = plugin_dir / "target" / "debug" / "wechat_client"
        if target_dir.exists():
            self.rust_binary_path = target_dir
            return True
        
        return False
    
    def _build_rust_binary(self):
        """编译 Rust 二进制文件"""
        plugin_dir = Path(__file__).parent
        logger.info(f"开始编译 Rust 程序...")
        
        try:
            result = subprocess.run(
                ["cargo", "build", "--release"],
                cwd=plugin_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("Rust 程序编译成功")
                return True
            else:
                logger.error(f"编译失败: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.error("编译超时")
            return False
        except FileNotFoundError:
            logger.error("未找到 cargo 命令，请先安装 Rust")
            return False
        except Exception as e:
            logger.error(f"编译过程出错: {e}")
            return False
    
    def _setup_handlers(self):
        """设置请求处理器"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """列出可用的工具"""
            return [
                Tool(
                    name="publish_to_wechat",
                    description="将本地 Markdown 文档发布到微信公众平台。文档路径可以是相对路径或绝对路径。如果文档包含 frontmatter（YAML 格式的元数据），将自动使用其中的 title、author、cover、theme 等配置。",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_path": {
                                "type": "string",
                                "description": "要发布的 Markdown 文档路径（相对路径或绝对路径）"
                            }
                        },
                        "required": ["document_path"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
            """处理工具调用"""
            try:
                logger.info(f"调用工具: {name}, 参数: {arguments}")
                
                if name == "publish_to_wechat":
                    return await self._handle_publish_to_wechat(arguments)
                else:
                    raise ValueError(f"未知的工具: {name}")
            
            except Exception as e:
                logger.error(f"工具调用失败: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"错误: {str(e)}"
                )]
    
    async def _handle_publish_to_wechat(self, arguments: dict) -> Sequence[TextContent]:
        """处理微信发布请求"""
        document_path = arguments.get("document_path")
        
        if not document_path:
            return [TextContent(
                type="text",
                text="错误: 文档路径不能为空"
            )]
        
        # 检查配置
        if not hasattr(self, 'app_id') or not hasattr(self, 'app_secret'):
            return [TextContent(
                type="text",
                text=f"错误: 请先配置 AppID 和 AppSecret。配置文件路径: {self.config_path}"
            )]
        
        # 解析文档路径
        doc_path = Path(document_path)
        if not doc_path.is_absolute():
            # 相对路径，相对于项目根目录
            project_root = Path(__file__).parent.parent.parent
            doc_path = project_root / document_path
        
        if not doc_path.exists():
            return [TextContent(
                type="text",
                text=f"错误: 文档不存在: {doc_path}"
            )]
        
        # 查找或编译 Rust 二进制文件
        if not self._find_rust_binary():
            logger.info("未找到已编译的二进制文件，开始编译...")
            if not self._build_rust_binary():
                return [TextContent(
                    type="text",
                    text="错误: 无法编译 Rust 程序。请确保已安装 Rust 和 cargo，并在插件目录运行 'cargo build --release'"
                )]
            self._find_rust_binary()
        
        if not self.rust_binary_path:
            return [TextContent(
                type="text",
                text="错误: 无法找到 Rust 二进制文件"
            )]
        
        # 调用 Rust 程序
        try:
            logger.info(f"调用 Rust 程序: {self.rust_binary_path}")
            logger.info(f"文档路径: {doc_path}")
            
            result = await asyncio.create_subprocess_exec(
                str(self.rust_binary_path),
                str(doc_path),
                self.app_id,
                self.app_secret,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='ignore')
                logger.error(f"Rust 程序执行失败: {error_msg}")
                return [TextContent(
                    type="text",
                    text=f"发布失败: {error_msg}"
                )]
            
            # 解析输出（JSON 格式）
            output = stdout.decode('utf-8', errors='ignore').strip()
            try:
                result_data = json.loads(output)
                draft_id = result_data.get('draft_id', '')
                
                success_msg = f"✅ 文章发布成功！\n\n"
                success_msg += f"草稿 ID: {draft_id}\n\n"
                success_msg += f"你可以在微信公众平台后台查看和管理这篇草稿。\n"
                success_msg += f"文档路径: {doc_path}\n"
                
                logger.info(f"发布成功，草稿 ID: {draft_id}")
                return [TextContent(
                    type="text",
                    text=success_msg
                )]
            except json.JSONDecodeError:
                # 如果不是 JSON，直接返回输出
                return [TextContent(
                    type="text",
                    text=f"发布完成: {output}"
                )]
        
        except Exception as e:
            logger.error(f"调用 Rust 程序失败: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=f"发布失败: {str(e)}"
            )]
    
    async def run(self):
        """运行服务器"""
        logger.info("启动 WeChat Pub MCP Server...")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """主函数"""
    server = WeChatPubMCPServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"服务器运行失败: {e}", exc_info=True)
        sys.exit(1)

