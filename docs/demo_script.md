# Sentio-AI Demo 视频讲解稿

> 约4分钟 / 边操作边解说

---

## 1. 启动前后端（30秒）
> 画面：VS Code → 两个终端分别启动

```
cd backend && python app.py    → Flask :5000
cd frontend && npm run dev     → Vite :5173
```

---

## 2. 登录（20秒）
> 画面：浏览器 localhost:5173 → 输入 shuhu / shuhuNB560 → 登录

JWT + bcrypt 认证，进入主界面。

---

## 3. 摄像头 + 对话（40秒）
> 画面：点摄像头 → 输入"你看到了什么？" → AI 根据画面回答

getUserMedia 获取画面，视觉模型分析。三种实时滤镜可切换。

---

## 4. API 直连（20秒）
> 画面：设置 → API 直连 → 开 → 填 Key → 保存

支持 OpenAI 兼容接口，浏览器直接调 API。

---

## 5. 语音输入（25秒）
> 画面：点麦克风 → 说话 → 自动转文字 → 自动发送 → AI 回复

MediaRecorder 录音 → STT → 文字 → 对话。

---

## 6. 截图 + 前后对比（35秒）
> 画面：点截图→AI分析 → 工具栏拍两张→对比差异

---

## 7. 对话管理 + 退出（25秒）
> 画面：新建对话 → 删除弹窗 → 退出登录

---

## 8. 线上部署（25秒）
> 画面：https://shuhu.me → HTTPS锁 → 摄像头正常

GitHub Pages + PythonAnywhere + 自定义域名。

---

## 9. 结尾（15秒）
> 画面：GitHub commit 记录

14次 commit，全周期交付，主分支可运行。感谢观看。
