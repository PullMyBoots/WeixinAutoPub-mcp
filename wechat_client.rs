use anyhow::Result;
use wechat_pub_rs::{WeChatClient, UploadOptions};
use std::env;

#[tokio::main]
async fn main() -> Result<()> {
    // 从命令行参数获取文档路径、AppID 和 AppSecret
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 4 {
        eprintln!("用法: {} <文档路径> <AppID> <AppSecret>", args[0]);
        std::process::exit(1);
    }
    
    let document_path = &args[1];
    let app_id = &args[2];
    let app_secret = &args[3];
    
    // 检查文档是否存在
    if !std::path::Path::new(document_path).exists() {
        eprintln!("错误: 文档不存在: {}", document_path);
        std::process::exit(1);
    }
    
    // 创建客户端
    let client = match WeChatClient::new(app_id, app_secret).await {
        Ok(client) => client,
        Err(e) => {
            eprintln!("错误: 客户端创建失败: {:?}", e);
            std::process::exit(1);
        }
    };
    
    // 检查是否有 frontmatter
    let content = match std::fs::read_to_string(document_path) {
        Ok(content) => content,
        Err(e) => {
            eprintln!("错误: 无法读取文档: {:?}", e);
            std::process::exit(1);
        }
    };
    
    let has_frontmatter = content.starts_with("---");
    
    // 上传文章
    let draft_id = if has_frontmatter {
        // 使用 frontmatter 中的配置
        match client.upload(document_path).await {
            Ok(id) => id,
            Err(e) => {
                eprintln!("错误: 文章上传失败: {:?}", e);
                std::process::exit(1);
            }
        }
    } else {
        // 使用默认配置
        let options = UploadOptions::with_theme("lapis")
            .comments(true, false);
        
        match client.upload_with_options(document_path, options).await {
            Ok(id) => id,
            Err(e) => {
                eprintln!("错误: 文章上传失败: {:?}", e);
                std::process::exit(1);
            }
        }
    };
    
    // 输出草稿 ID（JSON 格式，方便解析）
    println!("{{\"success\": true, \"draft_id\": \"{}\"}}", draft_id);
    
    Ok(())
}

