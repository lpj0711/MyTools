import os
import pydot

def convert_dot_to_png(dot_path):
    # 检查文件是否存在
    if not os.path.exists(dot_path):
        print(f'文件不存在: {dot_path}')
        return

    # 读取并修正中文编码
    with open(dot_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加中文字体配置
    modified_content = content.replace(
        'digraph {', 
        'digraph {\n    graph [fontname="Microsoft YaHei"];\n    node [fontname="Microsoft YaHei"];\n    edge [fontname="Microsoft YaHei"];'
    )

    # 生成PNG路径
    png_path = os.path.splitext(dot_path)[0] + '.png'
    
    try:
        # 通过graphviz生成图片
        (graph,) = pydot.graph_from_dot_data(modified_content)
        graph.write_png(png_path)
        print(f'已生成: {png_path}')
    except Exception as e:
        print(f'转换失败: {str(e)}')
        print('请确认已安装Graphviz并添加至系统PATH')

if __name__ == '__main__':
    sample_dot = r'AST_windows_deepseek.dot'  # 示例文件
    convert_dot_to_png(sample_dot)