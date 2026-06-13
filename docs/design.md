# AI 视觉对话助手 - 设计文档

> Author: shuhuNB560 / shuhuNB515
> 比赛题目：AI 视觉对话助手

---

## 一、项目概述

Sentio-AI 是一款**实时视觉 AI 对话助手**。用户打开摄像头与麦克风后，AI 能实时看到画面、听到声音，并给予多模态回应。支持文字/语音/图片三种输入方式，内置5种快捷视觉分析，支持对话历史管理和个性化设置。

**部署地址**: [https://shuhu.me](https://shuhu.me)
**GitHub**: [https://github.com/shuhuNB515/Sentio-AI](https://github.com/shuhuNB515/Sentio-AI)
**Demo 视频**: [百度网盘](https://pan.baidu.com/s/12GxFtEJNVGS-Myr2huvjgg?pwd=ixpx)（提取码: ixpx）

**技术栈：**
- 前端：Vue 3 (Composition API) + Vite + Vue Router + Axios
- 后端：Flask (Python 3.11) + Flask-JWT-Extended + SQLite
- AI：MIMO API (OpenAI 兼容协议)
- 部署：GitHub Pages + PythonAnywhere + 自定义域名 shuhu.me

---

## 二、用户故事

### 计划 vs 实现

| 编号 | 用户故事 | 优先级 | 状态 |
|------|---------|--------|------|
| US1 | 打开摄像头，让AI看到画面并理解环境 | P0 | ✅ 已实现 |
| US2 | 通过语音与AI对话，解放双手 | P0 | ✅ 已实现 |
| US3 | 通过文字与AI对话，兼容各种环境 | P0 | ✅ 已实现 |
| US4 | 听到AI的语音回复（TTS） | P1 | ✅ 已实现 |
| US5 | AI结合当前摄像头画面回答问题 | P0 | ✅ 已实现 |
| US6 | 查看对话历史消息，回顾上下文 | P1 | ✅ 已实现 |
| US7 | 开启/关闭语音播报，灵活切换 | P1 | ✅ 已实现 |
| US8 | 手动截图发送给AI进行深度分析 | P1 | ✅ 已实现 |
| US9 | 注册登录，保存对话历史和偏好 | P0 | ✅ 已实现 |
| US10 | 侧边栏管理对话（新建/切换/删除/归档） | P1 | ✅ 已实现 |
| US11 | 一键快捷视觉操作（描述/OCR/物体/翻译/情绪） | P0 | ✅ 已实现 |
| US12 | 自动检测语音起止（VAD静音检测） | P1 | ✅ 已实现 |
| US13 | 自动定期采样摄像头画面 | P2 | ✅ 已实现 |
| US14 | 纯文本和含图对话使用不同模型路由 | P1 | ✅ 已实现 |
| US15 | 设置面板调整参数（帧率/画质/TTS/模型） | P2 | ✅ 已实现 |
| US16 | 前后两张图像对比分析（拍到变化） | P2 | ✅ 已实现 |
| US17 | 摄像头实时滤镜（赛博/复古/素描） | P2 | ✅ 已实现 |
| US18 | 响应式布局适配手机和平板 | P2 | ✅ 已实现 |
| US19 | 输入自己的API Key直连大模型 | P2 | ✅ 已实现（原创） |
| US20 | 查看用量统计 | P2 | ✅ 已实现 |

**全部20个用户故事均已实现。**

---

## 三、成本控制策略

### 计划 vs 实际采用

| 编号 | 策略 | 原理 | 采用 |
|------|------|------|------|
| C1 | 帧采样间隔 | 非每帧发送，按固定间隔（5秒）采样 | ✅ |
| C2 | 图像压缩 | 前端缩放到max 640px + JPEG quality 70% | ✅ |
| C3 | 后端二次压缩 | 后端再压至512px + quality 70%，降token | ✅ |
| C4 | 低细节模式 | vision API 使用 `detail:"low"`（85 tokens vs 765+） | ✅ |
| C5 | 模型路由 | 纯文本用 flash 模型，含图用 omni 模型 | ✅ |
| C6 | 相似帧缓存 | MD5哈希比对，命中直接返回 | ✅ |
| C7 | 历史裁剪 | 只保留最近10轮，控制上下文token | ✅ |
| C8 | VAD静音检测 | 静音2秒自动停止录音，不发空白音频 | ✅ |
| C9 | 限流控制 | 每分钟最多20次API调用 | ✅ |
| C10 | 视觉上下文摘要 | 纯文本对话注入摘要而非图像 | ✅ |
| C11 | 前端直连模式 | 浏览器直调API，不走后端中转 | ✅（原创） |
| C12 | JWT无状态认证 | 减少数据库Session查询 | ✅ |
| C13 | SQLite WAL模式 | 支持并发读写，按需连接 | ✅ |

**采用了13种策略，未采用的有：**
- 批量帧对比（复杂度高，收益有限）
- 本地OCR预处理（增加部署复杂度）
- 语义缓存（误判风险高）

### 核心策略详解

**1. 模型路由**：纯文本对话用 `mimo-v2-flash`（快速/便宜），含图像时用 `mimo-v2-omni`（视觉理解）。flash 成本约为 omni 的 1/5~1/10。

**2. 低细节模式**：`detail: "low"` 固定消耗 85 tokens/图，`"high"` 可能 765+ tokens/图，节省约 89%。

**3. 图像压缩链路**：前端 Canvas reduce → JPEG 70% → 后端 Pillow resize 512px → JPEG 70%，原图约8MB → 最终约15KB，传输量减少 99.8%。

**4. 视觉上下文摘要**：摄像头定时采样 → 生成描述摘要 → 存为 system 消息。后续纯文本对话只需注入摘要，无需每次都发图。将视觉调用从"每轮1次"降到"每5秒1次"。

**5. 前端直连模式（原创）**：用户自配 API Key，浏览器 `fetch()` 直调 AI API。绕过后端中转，消除 PythonAnywhere 免费版网络白名单限制，同时减少后端服务器负载。

---

## 四、系统架构

```
浏览器 (Vue3 SPA)
├── LoginPage        # 登录/注册（JWT + bcrypt）
├── MainPage         # 主界面
│   ├── CameraView   # 摄像头（getUserMedia + Canvas滤镜）
│   ├── ChatPanel    # 对话面板（文字/语音/图片）
│   ├── VoiceInput   # 语音输入（MediaRecorder + STT）
│   ├── CreativeToolbar  # 创意工具（前后对比/滤镜/语音命令）
│   ├── RecognitionPanel # 识别记录展示
│   ├── Sidebar      # 对话列表管理
│   └── SettingsModal    # 设置面板（含API直连配置）
├── api/index.js     # 后端 API 封装
└── services/directApi.js  # 前端直连 AI 服务

        │ HTTP + JWT
        ▼

Flask REST API (PythonAnywhere)
├── app.py           # 路由入口 + JWT认证
├── config.py        # 配置管理（环境变量）
├── services/
│   ├── chat.py      # 对话引擎（上下文管理/模型路由）
│   ├── vision.py    # 视觉分析（场景/OCR/物体/翻译/情绪）
│   ├── speech.py    # 语音识别(STT) + 语音合成(TTS)
│   ├── database.py  # SQLite ORM（用户/会话/消息/截图）
│   └── cost_control.py  # 限流/统计/速率控制

        │
        ▼

MIMO AI API (OpenAI 兼容)
├── mimo-v2-omni     # 视觉理解模型
├── mimo-v2-flash    # 快速对话模型
├── mimo-v2.5-asr    # 语音识别
└── mimo-v2.5-tts    # 语音合成
```

### 数据流

```
用户输入 → 前端处理 → 后端路由 → AI服务 → 后端响应 → 前端渲染
                     ↘ 直连模式：浏览器 fetch → AI API
```

---

## 五、API 接口设计

| 分类 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 认证 | `/api/auth/register` | POST | 用户注册 |
| | `/api/auth/login` | POST | 登录（返回JWT） |
| | `/api/auth/me` | GET | 当前用户信息 |
| | `/api/auth/settings` | PUT | 保存设置 |
| 会话 | `/api/conversations` | GET/POST | 列表/新建 |
| | `/api/conversations/<id>` | GET/PUT/DELETE | 详情/更新/删除 |
| 对话 | `/api/chat` | POST | 文本/图文对话 |
| | `/api/multimodal` | POST | 多模态对话（含TTS） |
| 视觉 | `/api/vision/quick` | POST | 快捷分析（5种） |
| 语音 | `/api/stt` | POST | 语音识别 |
| | `/api/tts` | POST | 语音合成 |
| 截图 | `/api/screenshots` | GET/POST | 列表/保存 |
| 统计 | `/api/stats` | GET | 用量统计 |
| 健康 | `/api/health` | GET | 健康检查 |

---

## 六、数据库设计 (SQLite)

```
users(id, username, password_hash, avatar_color, created_at, last_login, settings)
conversations(id, user_id, title, created_at, updated_at, is_archived)
messages(id, conversation_id, role, content, has_image, image_path, created_at)
screenshots(id, user_id, conversation_id, image_path, description, created_at)
```

---

## 七、部署方案

| 组件 | 平台 | 地址 |
|------|------|------|
| 前端 | GitHub Pages | https://shuhuNB515.github.io/Sentio-AI/ |
| 后端 | PythonAnywhere | https://shuhuNB666.pythonanywhere.com |
| 域名 | Namecheap DNS | https://shuhu.me (A记录→GitHub Pages IP) |
| 构建 | GitHub Actions | 自动构建+部署到 gh-pages 分支 |

---

## 八、Commit 与 PR 记录

全周期持续交付：2026-06-12 ~ 2026-06-13，16次 commit + 8个 PR。

| # | 日期 | 内容 |
|---|------|------|
| PR#1 | 06-12 23:27 | 项目初始化：Vue3 + Flask 骨架 |
| PR#2 | 06-12 23:30 | 部署配置：GitHub Actions + Pages |
| PR#3 | 06-12 23:48 | 前后端对接：API协议匹配、字体优化 |
| PR#4 | 06-13 00:11 | 摄像头/麦克风：HTTP安全检测、图片路径 |
| PR#5 | 06-13 13:52 | HTTPS安全：isSecureContext检测+徽章 |
| PR#6 | 06-13 15:12 | 自定义域名：相对路径+CNAME+模型名 |
| PR#7 | 06-13 16:17 | API直连模式：用户自配Key（原创） |
| PR#8 | 06-13 16:40 | 文档完善：README+设计文档+Demo稿 |

---

## 九、创新点

1. **前端API直连**：首创用户自配Key/URL/Model，浏览器直调AI，绕过后端网络限制
2. **11种成本控制策略组合**：帧采样+压缩+低细节+模型路由+缓存+裁剪+摘要+VAD+限流+直连+JWT
3. **视觉上下文摘要注入**：定时采样→生成摘要→注入纯文本对话，大幅降低视觉调用
4. **前后图像对比分析**：拍两张→分别描述→AI对比差异，适合场景变化检测
5. **实时Canvas滤镜**：赛博朋克/复古/素描三种像素级处理滤镜
6. **完整语音链路**：MediaRecorder→STT→对话→TTS→Audio播放
