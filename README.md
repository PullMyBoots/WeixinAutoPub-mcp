# WeChat Pub MCP Server

微信公众平台文章发布 MCP 服务器，支持一键将本地 Markdown 文档发布到微信公众平台。

## 快速开始

### 1. 配置凭证

编辑 `config.txt` 文件，设置你的微信公众平台凭证：

```
AppID:your_app_id
AppSecret:your_app_secret
```

### 2. 编译 Rust 程序（首次使用）

```bash
cd plug_in/WeChat_Pub
cargo build --release
```

### 3. 使用 MCP 工具

在 Cursor 或其他支持 MCP 的 IDE 中，调用工具：

```
publish_to_wechat(document_path="daily_report/2025-11-08.md")
```

## 功能特性

- ✅ 一键发布：只需提供文档路径即可发布
- ✅ 自动读取配置：从 `config.txt` 读取 AppID 和 AppSecret
- ✅ 支持 Frontmatter：自动读取 Markdown 文件中的元数据（title、author、cover、theme）
- ✅ 自动处理图片：自动上传文章中的本地图片到微信服务器
- ✅ 智能去重：相同图片只上传一次

## 使用方法

### MCP 工具调用

工具名称：`publish_to_wechat`

参数：
- `document_path` (必需): Markdown 文档路径（相对路径或绝对路径）

示例：

```python
# 使用相对路径（相对于项目根目录）
publish_to_wechat(document_path="daily_report/2025-11-08.md")

# 使用绝对路径
publish_to_wechat(document_path="/Users/username/Desktop/article.md")
```

## Markdown 文档格式

### 基本格式

```markdown
# 文章标题

文章内容...
```

### 带 Frontmatter 的格式（推荐）

```markdown
---
title: "文章标题"
author: "作者名称"
cover: "/绝对路径/封面图片.jpg"
theme: "lapis"
---

# 文章标题

文章内容...
```

### Frontmatter 字段说明

- `title`: 文章标题
- `author`: 作者名称
- `cover`: 封面图片路径（必须使用绝对路径）
- `theme`: 主题名称（可选，默认：`lapis`）

**可选主题列表**（共 8 种）：

1. **`lapis`** - 蓝色主题（默认，推荐）
2. **`github`** - GitHub 风格，简洁明亮
3. **`monokai`** - Monokai 风格，经典暗色
4. **`solarized-dark`** - Solarized 深色主题
5. **`solarized-light`** - Solarized 浅色主题
6. **`dracula`** - Dracula 风格，紫色调暗色
7. **`nord`** - Nord 风格，冷色调
8. **`one-dark`** - One Dark 风格，深色主题

### 在文章中插入图片

使用标准 Markdown 图片语法，**必须使用绝对路径**：

```markdown
![图片描述](/绝对路径/图片.jpg)
```

**注意**：wechat-pub-rs 出于安全考虑，不允许使用相对路径（如 `../images/`），必须使用绝对路径。

## 返回结果

成功时返回：

```
✅ 文章发布成功！

草稿 ID: xxxxxx

你可以在微信公众平台后台查看和管理这篇草稿。
文档路径: /path/to/document.md
```

## 故障排除

### 1. 编译失败

确保已安装 Rust：
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### 2. 配置错误

检查 `config.txt` 文件格式是否正确，确保包含 AppID 和 AppSecret。

### 3. 文档路径错误

- 相对路径：相对于项目根目录
- 绝对路径：完整的文件系统路径

### 4. 图片路径错误

所有图片路径必须使用绝对路径，不能使用 `../` 这样的相对路径。

## 技术架构

1. **Python MCP Server**: 处理 MCP 协议，调用 Rust 程序
2. **Rust Client**: 使用 wechat-pub-rs 库上传文章
3. **配置文件**: 存储 AppID 和 AppSecret

## 注意事项

1. ⚠️ **凭证安全**: `config.txt` 包含敏感信息，不要提交到版本控制
2. ⚠️ **图片路径**: 必须使用绝对路径
3. ⚠️ **API 限制**: 注意微信公众平台的 API 调用频率限制
4. ⚠️ **网络要求**: 需要能够访问微信服务器

## 依赖

- Python 3.8+
- Rust 1.70+
- wechat-pub-rs 0.6.0
- MCP SDK

## 许可证

MIT

