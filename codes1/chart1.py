import xml.etree.ElementTree as ET

# 输入 JSON 数据
data = {
    "nodes": [
        {"id": "start", "label": "Start", "type": "start"},
        {"id": "decision", "label": "x > 10?", "type": "decision"},
        {"id": "return_x", "label": "Return x", "type": "process"},
        {"id": "return_0", "label": "Return 0", "type": "process"},
        {"id": "end", "label": "End", "type": "end"}
    ],
    "connections": [
        {"from": "start", "to": "decision"},
        {"from": "decision", "to": "return_x", "label": "Yes"},
        {"from": "decision", "to": "return_0", "label": "No"},
        {"from": "return_x", "to": "end"},
        {"from": "return_0", "to": "end"}
    ]
}

import zipfile
import json
import os

# 创建 VSDX 文件到当前目录
def create_vsdx(data):
    # 创建 JSON 文件
    with open("diagram.json", "w") as json_file:
        json.dump(data, json_file)

    # 创建 VSDX 压缩包
    with zipfile.ZipFile("output.vsdx", "w", zipfile.ZIP_DEFLATED) as vsdx:
        vsdx.write("diagram.json", "diagram.json")

    # 清理 JSON 文件
    os.remove("diagram.json")

# 生成 VSDX 文件
create_vsdx(data)

print("Visio VSDX 文件已创建为 output.vsdx!")
