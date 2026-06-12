#!/usr/bin/env python
# Sentio-AI WSGI 入口 - PythonAnywhere 部署
# Author: shuhuNB560 / shuhuNB515
#
# 使用方法:
#   1. 在 PythonAnywhere Web 面板中，将 Source code 路径设为项目根目录
#   2. Working directory: /home/shuhuNB666/Sentio-AI/backend
#   3. WSGI configuration file 指向此文件

import sys
import os

# 项目路径
project_dir = '/home/shuhuNB666/Sentio-AI/backend'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# 确保加载 .env 中的环境变量
from dotenv import load_dotenv
dotenv_path = os.path.join(project_dir, '.env')
load_dotenv(dotenv_path)

# 创建 data 目录（如果不存在）
data_dir = os.path.join(project_dir, 'data')
os.makedirs(data_dir, exist_ok=True)

from app import app as application
