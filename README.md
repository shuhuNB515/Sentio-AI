# Sentio-AI — 视觉 AI 对话助手

> **Author**: shuhuNB560 / shuhuNB515
> **Live**: [https://shuhu.me](https://shuhu.me) | [GitHub Pages](https://shuhuNB515.github.io/Sentio-AI/)

Sentio-AI 是一个**实时视觉 + 语音 + 对话**的全栈 AI 助手。它能通过摄像头看到你的画面，通过麦克风听到你的声音，并结合 AI 模型进行自然语言回复。

---

## 功能一览

| 模块 | 功能 | 实现方式 |
|------|------|----------|
| 🎥 摄像头 | 实时画面捕获、滤镜效果（赛博/复古/素描） | `getUserMedia` + Canvas 处理 |
| 🎤 语音输入 | 录音 → 语音识别 → 自动发送 | `MediaRecorder` + STT API |
| 🔊 语音合成 | AI 回复自动朗读 | TTS API → `Audio` 播放 |
| 💬 多模态对话 | 文字+图片+语音综合对话 | OpenAI 兼容 API（视觉模型） |
| 📷 截图分析 | 一键截图 → AI 描述画面 | 视觉模型 scene description |
| 🔍 快捷视觉 | 场景描述 / OCR / 物体识别 / 翻译 / 情绪分析 | 五个独立 prompt |
| ⚡ 前后对比 | 拍两张照片 → AI 分析变化 | 两次视觉调用 + 对比 prompt |
| 🎨 创意工具栏 | 语音命令 / 滤镜切换 / 截图对比 | 语音指令映射到功能 |
| 📋 对话管理 | 新建/切换/删除/归档对话 | SQLite + CRUD API |
| ⚙️ 设置面板 | 帧率/画质/模型/TTS 可调，API Key 自配 | 本地缓存 + 后端同步 |
| 🔑 API 直连 | 前端直连 AI API，绕过后端代理受限 | `fetch()` + 用户自配 Key |

---

## 技术架构

```
┌─────────────────────────────────────────────────┐
│                    浏览器                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Camera   │ │   Audio   │ │   Chat UI (Vue3) │ │
│  │ getUser  │ │ MediaRec │ │   ├─ 直连模式     │ │
│  │ Media()  │ │ order()  │ │   └─ 后端模式     │ │
│  └──────────┘ └──────────┘ └──────┬───────────┘ │
└──────────────────────────────────┼──────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │    Flask REST API (Python)    │
                    │  ├─ JWT 认证 + SQLite 存储    │
                    │  ├─ 对话路由 + 会话管理        │
                    │  ├─ 视觉/语音服务转发          │
                    │  └─ 成本控制 + 限流            │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │   MIMO AI API (OpenAI 兼容)   │
                    │  ├─ mimo-v2-omni (视觉)       │
                    │  ├─ mimo-v2-flash (对话)      │
                    │  ├─ mimo-v2.5-asr (语音识别)  │
                    │  └─ mimo-v2.5-tts (语音合成)  │
                    └─────────────────────────────┘
```

---

## 第三方依赖

### 前端

| 依赖 | 版本 | 用途 |
|------|------|------|
| Vue 3 | ^3.4.0 | UI 框架（Composition API） |
| Vue Router | ^4.6.4 | 前端路由 (/#/login, /#/chat) |
| Axios | ^1.17.0 | HTTP 请求库 |
| Vite | ^5.4.0 | 构建工具 |
| @vitejs/plugin-vue | ^5.0.0 | Vite Vue 插件 |

### 后端

| 依赖 | 版本 | 用途 |
|------|------|------|
| Flask | >=3.0.0 | Web 框架 |
| flask-cors | >=4.0.0 | 跨域请求处理 |
| flask-jwt-extended | >=4.6.0 | JWT 用户认证 |
| openai | >=1.30.0 | OpenAI 兼容 API 客户端 |
| Pillow | >=10.0.0 | 图像压缩处理 |
| python-dotenv | >=1.0.0 | 环境变量加载 |
| bcrypt | >=4.1.0 | 密码哈希 |
| requests | >=2.28.0 | HTTP 请求 |

### 无第三方外部版权素材

所有前端静态资源（bg.png, alert.png, pay.png, avatar.png）均为原创素材。

---

## 原创功能说明

| 功能 | 原创实现 |
|------|----------|
| **前端直连 API 模式** | 完全原创：用户自配 API Key/Base URL/Model，浏览器直接调用 OpenAI 兼容 API，绕过后端代理受限 |
| **多模态对话引擎** | 原创：统一管理视觉上下文摘要 + 对话历史裁剪 + 模型自动路由（图片→视觉模型，文本→对话模型） |
| **实时摄像头滤镜** | 原创：Canvas 像素级处理，支持赛博朋克/复古/素描三种实时滤镜 |
| **语音命令系统** | 原创：Web Speech API + 关键词映射（"截图"/"描述"/"翻译"等） |
| **前后图像对比** | 原创：抓取两个时间点帧 → 分别 AI 描述 → 对比分析差异 |
| **成本控制系统** | 原创：帧采样间隔控制、图像质量压缩、对话历史裁剪、相似帧缓存、API 限流 |
| **响应式适配** | 原创：桌面/平板/手机三档自适应，视觉区可拖拽调整宽度 |

---

## 快速启动

### 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
cp .env.example .env   # 编辑 .env 填入 API Key
python app.py           # → http://localhost:5000

# 前端
cd frontend
npm install
npm run dev             # → http://localhost:5173
```

### 环境变量 (.env)

```env
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.xiaomimimo.com/v1
CORS_ORIGINS=http://localhost:5173,https://shuhu.me
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

### 生产部署

- **前端**: GitHub Pages（自动构建，`.github/workflows/deploy.yml`）
- **后端**: PythonAnywhere（WSGI + virtualenv）
- **域名**: shuhu.me（DNS A 记录 → GitHub Pages IP）

---

## 项目结构

```
Sentio-AI/
├── .github/workflows/deploy.yml    # GitHub Actions 自动部署
├── frontend/                       # Vue 3 前端
│   ├── src/
│   │   ├── api/index.js            # 后端 API 封装
│   │   ├── services/directApi.js   # 前端直连 AI 服务
│   │   ├── composables/useAuth.js  # 认证状态管理
│   │   ├── components/             # UI 组件
│   │   └── views/                  # 页面（登录/主界面）
│   └── vite.config.js              # Vite 配置
├── backend/                        # Flask 后端
│   ├── app.py                      # 路由 + 入口
│   ├── config.py                   # 配置管理
│   ├── services/                   # 业务服务
│   │   ├── chat.py                 # 对话引擎
│   │   ├── vision.py               # 视觉分析
│   │   ├── speech.py               # 语音识别/合成
│   │   ├── database.py             # SQLite 数据库
│   │   └── cost_control.py         # 成本控制
│   └── wsgi.py                     # PythonAnywhere WSGI 入口
└── docs/design.md                  # 设计文档
```

---

## Commit 记录

本项目遵循小粒度 PR 原则，以下为全周期持续交付记录（2026-06-12 ~ 2026-06-13）：

| # | Commit | 日期 | 内容 |
|---|--------|------|------|
| 1 | `dbbbb12` | 06-12 23:27 | 初始化项目：Vue3 + Flask + 摄像头/语音 |
| 2 | `c53749a` | 06-12 23:30 | 部署配置：GitHub Pages + PythonAnywhere |
| 3 | `7b6fc69` | 06-12 23:43 | GitHub Actions 手动触发 |
| 4 | `36eb8c0` | 06-12 23:48 | 移除 Google Fonts、修复 API 协议匹配 |
| 5 | `48dc10d` | 06-12 23:54 | 补充 requests 依赖 |
| 6 | `e1e7370` | 06-13 00:03 | 添加后端根路由 |
| 7 | `858bcbf` | 06-13 00:11 | 修复图片路径（GitHub Pages 子路径） |
| 8 | `d7d819c` | 06-13 00:14 | 摄像头/麦克风 HTTP 错误提示 |
| 9 | `314ba8e` | 06-13 13:52 | isSecureContext 检测 + HTTP/HTTPS 徽章 |
| 10 | `731a2a5` | 06-13 15:12 | 相对路径兼容自定义域名 |
| 11 | `22b967d` | 06-13 15:16 | CNAME 文件支持自定义域名 |
| 12 | `d97d129` | 06-13 15:31 | MIMO API 模型名修正 |
| 13 | `a7872b5` | 06-13 16:17 | 前端直连 API 模式 |

---

## License

此项目为原创作品，版权所有 © 2026 shuhuNB560
