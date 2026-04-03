# -*- coding: utf-8 -*-  

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from paddleocr import PPStructureV3
import uvicorn
import os
from markdown_to_docx import markdown_to_docx_with_images

'''
    该项目基于PaddleOCR实现PDF转Markdown功能。
    项目结构：
    - app.py: 主应用文件，定义了FastAPI应用和路由。
    - static/: 静态文件目录，包含前端页面。
    - uploads/: 上传文件目录，用于存储上传的PDF文件。
    - output/: 输出文件目录，用于存储转换后的Markdown文件。
'''

app = FastAPI()

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/convert")
async def convert_pdf_to_markdown(file: UploadFile = File(...)):
    """
    接收PDF文件并转换为Markdown
    """
    # 保存上传的PDF文件
    pdf_path = Path("temp.pdf")
    with open(pdf_path, "wb") as f:
        f.write(await file.read())
    
    # 处理PDF
    pipeline = PPStructureV3()
    output = pipeline.predict(str(pdf_path))
    
    markdown_list = []
    for res in output:
        save_img(res.markdown)
        print(res.markdown)
        markdown_list.append(res.markdown)
    
    markdown_texts = pipeline.concatenate_markdown_pages(markdown_list)
    
    # 保存Markdown文件
    mkd_file_path = Path("output") / f"{Path(file.filename).stem}.md"
    mkd_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(mkd_file_path, "w", encoding="utf-8") as f:
        f.write(markdown_texts)
    save_docx(mkd_file_path)
    # 返回Markdown文件
    return FileResponse(mkd_file_path, media_type="text/markdown", filename=mkd_file_path.name)

def save_img(data):
    # 保存图片
    for img_path, img_obj in data['markdown_images'].items():
        # 创建目录（如果不存在）
        os.makedirs(Path("output")/os.path.dirname(img_path), exist_ok=True)
        # 保存图片
        img_obj.save(Path("output")/img_path)
        print(f"图片已保存到: {img_path}")

def save_docx(markdown_file):
    try:
        docx_path = markdown_to_docx_with_images(markdown_file)
        print(f"转换成功！生成的Word文档: {docx_path}")
    except Exception as e:
        print(f"转换失败: {e}")

@app.get("/", response_class=HTMLResponse)
async def get_upload_page():
    """
    返回前端上传页面
    """
    return """
    <!DOCTYPE html>
<html>
<head>
    <title>PDF转Markdown</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
        }
        .upload-area {
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
        }
        .upload-area:hover {
            border-color: #007bff;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .status {
            margin: 20px 0;
            padding: 10px;
            border-radius: 5px;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .loading {
            background-color: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
    </style>
    <script>
        async function handleSubmit(event) {
            event.preventDefault();
            
            const fileInput = document.querySelector('input[type="file"]');
            const submitButton = document.querySelector('button[type="submit"]');
            const statusDiv = document.getElementById('status');
            
            // 检查是否选择了文件
            if (!fileInput.files[0]) {
                showStatus('请选择一个PDF文件', 'error');
                return;
            }
            
            // 显示加载状态
            submitButton.disabled = true;
            submitButton.textContent = '转换中...';
            showStatus('正在转换PDF文件，请稍候...', 'loading');
            
            try {
                const formData = new FormData(event.target);
                const response = await fetch('/convert', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    // 获取上传文件的基本名称并替换扩展名为.md
                    const originalFilename = fileInput.files[0].name;
                    const baseName = originalFilename.substring(0, originalFilename.lastIndexOf('.')) || originalFilename;
                    let filename = baseName + '.md';
                    const contentDisposition = response.headers.get('Content-Disposition');
                    if (contentDisposition) {
                        const filenameMatch = contentDisposition.match(/filename=(.+)/);
                        if (filenameMatch) {
                            filename = filenameMatch[1].replace(/"/g, '');
                        }
                    }
                    
                    // 下载文件
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = filename;
                    a.style.display = 'none';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    
                    showStatus(`转换成功！文件 "${filename}" 已开始下载。`, 'success');
                } else {
                    const errorText = await response.text();
                    showStatus(`转换失败：${response.status} - ${errorText}`, 'error');
                }
            } catch (error) {
                showStatus(`网络错误：${error.message}`, 'error');
            } finally {
                // 恢复按钮状态
                submitButton.disabled = false;
                submitButton.textContent = '转换';
            }
        }
        
        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = `status ${type}`;
            statusDiv.style.display = 'block';
        }
        
        function handleFileChange(event) {
            const file = event.target.files[0];
            const statusDiv = document.getElementById('status');
            
            if (file) {
                if (file.type !== 'application/pdf') {
                    showStatus('请选择PDF文件', 'error');
                    event.target.value = '';
                    return;
                }
                
                const fileSize = (file.size / 1024 / 1024).toFixed(2);
                showStatus(`已选择文件：${file.name} (${fileSize} MB)`, 'success');
            } else {
                statusDiv.style.display = 'none';
            }
        }
    </script>
</head>
<body>
    <h1>PDF转Markdown工具</h1>
    <div class="upload-area">
        <form onsubmit="handleSubmit(event)" enctype="multipart/form-data">
            <p>选择PDF文件进行转换</p>
            <input type="file" name="file" accept=".pdf" required onchange="handleFileChange(event)">
            <br><br>
            <button type="submit">转换</button>
        </form>
    </div>
    
    <div id="status" class="status" style="display: none;"></div>
    
    <div style="margin-top: 30px; font-size: 14px; color: #666;">
        <h3>使用说明：</h3>
        <ul>
            <li>支持PDF文件转换为Markdown格式</li>
            <li>转换完成后会自动下载Markdown文件</li>
            <li>请确保PDF文件清晰可读，以获得最佳转换效果</li>
        </ul>
    </div>
</body>
</html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8083,log_level="debug")
