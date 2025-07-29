import argparse
import sys
from PyPDF2 import PdfReader, PdfWriter

# 安装命令: python -m pip install PyPDF2

def split_pdf(input_path, start_page, end_page, output_path):
    try:
        with open(input_path, 'rb') as file:
            reader = PdfReader(file)
            
            if end_page > len(reader.pages):
                end_page = len(reader.pages)
            # 验证页码范围
            if start_page < 1 or end_page > len(reader.pages) or start_page > end_page:
                raise ValueError("无效的页码范围")
            
            writer = PdfWriter()
            for i in range(start_page-1, end_page):
                writer.add_page(reader.pages[i])
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            print(f"成功保存拆分文件至: {output_path}")
    
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PDF文件拆分工具')
    parser.add_argument('--input', required=True, help='输入PDF文件路径')
    parser.add_argument('--start', type=int, required=True, help='起始页码（从1开始）')
    parser.add_argument('--end', type=int, required=True, help='结束页码')
    parser.add_argument('--output', required=True, help='输出文件路径')
    
    args = parser.parse_args()
    split_pdf(args.input, args.start, args.end, args.output)