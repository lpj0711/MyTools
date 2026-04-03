from PyQt5.QtCore import QTranslator, QCoreApplication

app = QCoreApplication([])
translator = QTranslator()

# 检查文件是否存在
import os
if not os.path.exists("AppTools_ja.qm"):
    raise FileNotFoundError("QM文件不存在，请先生成翻译文件")

if translator.load("AppTools_ja.qm"):
    app.installTranslator(translator)
else:
    print("QM文件加载失败，请检查文件格式")

# 调试输出
try:
    print(f"QM文件存在: {translator.__dict__['_QTranslator__translation']['Hash']}")
except KeyError:
    print("未找到有效翻译条目")
    print(f"翻译器结构: {translator.__dict__}")
    
# 提取所有翻译对 eeeeeeeeeeee1
translation_map = {}
# 遍历所有可能的翻译条目
for key in translator.__dict__.get('_QTranslator__translation', {}).get('Hash', {}):
    try:
        original = key.decode('utf-8')
        translated = translator.translate(None, original)
        if translated:
            translation_map[original] = translated
    except Exception as e:
        print(f"解码错误: {e}")

print(translation_map)