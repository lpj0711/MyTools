import comtypes.client

"""
使用 Microsoft Word 的 COM 接口将 .docx 文件转换为 .pdf 文件。

Args:
    input_path (str): 输入的 .docx 文件路径。
    output_path (str): 输出的 .pdf 文件路径。
"""

def docx_to_pdf(input_path, output_path):
    word = comtypes.client.CreateObject("Word.Application")
    doc = word.Documents.Open(input_path)
    doc.SaveAs(output_path, FileFormat=17)  # 17是PDF格式的代码
    doc.Close()
    word.Quit()



if __name__ == "__main__":
    input_file = r"C:\Users\liuwei\Downloads\北邮~结构图测试3.docx"
    output_file = r"C:\Users\liuwei\Downloads\北邮~结构图测试3.pdf"
    docx_to_pdf(input_file, output_file)
    print("转换完成")
