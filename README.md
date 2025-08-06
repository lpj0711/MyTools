# MyTools
   ## 保存python所有脚本
    1.neo4j_handle.py:解析AST代码，把结构转换成neo4j的cypher命令，存储到知识图谱
    2.deepseek_api.py:本地调用deepseek的API
    3.dot_to_png.py:dot文件转成png

# Git常用命令
```bash
   git init # 初始化仓库并设置远程链接
   git remote add origin <远程仓库的URL> # 添加远程仓库
   git remote -v # 查看远程仓库配置
   git fetch --all # 获取所有分支代码
   git add . # 获取所有分支代码
   git commit -m "你的提交说明" # 提交变更（附带提交信息）
   git push origin master # 推送代码到远程仓库主分支
   git pull origin master # 从远程仓库拉取代码
```
# docker命令
   ## vllm部署
   ```bash
      # 拉取镜像
      docker pull pytorch/pytorch:latest
      # 创建容器
      docker run --gpus all --name vllm -d -p 8081:8081 -v D:/codehub:/opt/  pytorch/pytorch:latest
      # 安装vLLM（支持AWQ量化）
      pip install vllm
      # 启动vllm服务器
      python -m vllm.entrypoints.openai.api_server  --model Qwen/Qwen3-8B-AWQ --tensor-parallel-size 1 --max-num-seqs 4 --max-model-len 4068 --port 8082
   ```
   ## paddle OCR部署
   ```bash
      # 拉取镜像
      docker pull nvidia/cuda:12.4.1-devel-ubuntu22.04
      # 创建容器
      docker run --gpus all --name paddleocr -d -p 8083:8083 -v D:/codehub:/workspace -w /workspace --tmpfs /tmp:rw,size=8g --shm-size=8g nvidia/cuda:12.4.1-devel-ubuntu22.04 tail -f /dev/null
      sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list
      sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list
      apt install -y python3 python3-pip
      ln -s /usr/bin/python3 /usr/bin/python
      apt-get update
      apt-get install -y libgl1
      apt-get install -y libgomp1
      pip install paddlepaddle-gpu==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
      pip install fastapi uvicorn python-multipart -i https://mirrors.aliyun.com/pypi/simple      
      pip install numpy==1.24.3 -i https://mirrors.aliyun.com/pypi/simple/
      apt update && apt install -y \
         libglib2.0-0 \
         libgtk-3-0 \
         libgdk-pixbuf2.0-0 \
         libgl1-mesa-glx \
         libsm6 \
         libxext6 \
         libxrender-dev \
         libgomp1 \
         fontconfig \
         libfontconfig1 \
         libfreetype6-dev \
         libharfbuzz-dev
   ```