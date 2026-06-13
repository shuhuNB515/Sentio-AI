/**
 * 媒体处理工具 - 摄像头、麦克风、帧采集
 */

// 请求摄像头权限并获取视频流
export async function startCamera(videoElement) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: 'user',
      },
      audio: false,
    })
    if (videoElement) {
      videoElement.srcObject = stream
      await videoElement.play()
    }
    return stream
  } catch (err) {
    console.error('摄像头启动失败:', err)
    throw new Error('无法访问摄像头，请检查权限设置')
  }
}

// 停止摄像头
export function stopCamera(stream) {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
  }
}

// 请求麦克风权限
export async function startMicrophone() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    })
    return stream
  } catch (err) {
    console.error('麦克风启动失败:', err)
    throw new Error('无法访问麦克风，请检查权限设置')
  }
}

// 停止麦克风
export function stopMicrophone(stream) {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
  }
}

// 从视频帧截取base64图像（带压缩）
export function captureFrame(videoElement, maxSize = 512, quality = 0.7) {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')

  let { videoWidth, videoHeight } = videoElement
  // 缩放
  const ratio = Math.min(maxSize / Math.max(videoWidth, videoHeight), 1)
  canvas.width = Math.round(videoWidth * ratio)
  canvas.height = Math.round(videoHeight * ratio)

  ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height)

  // 返回不带前缀的base64
  const dataUrl = canvas.toDataURL('image/jpeg', quality)
  return dataUrl.split(',')[1]
}

// 录音器类 - 使用MediaRecorder采集音频
export class AudioRecorder {
  constructor(stream) {
    this.stream = stream
    this.recorder = null
    this.chunks = []
    this.isRecording = false
  }

  start() {
    this.chunks = []
    // 优先使用webm格式
    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : 'audio/ogg'

    this.recorder = new MediaRecorder(this.stream, { mimeType })
    this.recorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        this.chunks.push(e.data)
      }
    }
    this.recorder.start(100) // 每100ms收集一次数据
    this.isRecording = true
  }

  stop() {
    return new Promise((resolve) => {
      if (!this.recorder || !this.isRecording) {
        resolve(null)
        return
      }
      this.recorder.onstop = () => {
        const blob = new Blob(this.chunks, { type: this.recorder.mimeType })
        this.isRecording = false
        resolve(blob)
      }
      this.recorder.stop()
    })
  }
}

// 简单VAD（语音活动检测）- 基于音量
export class VoiceActivityDetector {
  constructor(stream, options = {}) {
    this.threshold = options.threshold || 0.01
    this.silenceDuration = options.silenceDuration || 1500 // ms
    this.onSpeechStart = options.onSpeechStart || (() => {})
    this.onSpeechEnd = options.onSpeechEnd || (() => {})

    this.audioContext = null
    this.analyser = null
    this.source = null
    this.isSpeaking = false
    this.silenceTimer = null
    this.running = false
  }

  start(stream) {
    this.audioContext = new (window.AudioContext || window.webkitAudioContext)()
    this.source = this.audioContext.createMediaStreamSource(stream)
    this.analyser = this.audioContext.createAnalyser()
    this.analyser.fftSize = 512
    this.source.connect(this.analyser)
    this.running = true
    this._detect()
  }

  _detect() {
    if (!this.running) return

    const data = new Float32Array(this.analyser.fftSize)
    this.analyser.getFloatTimeDomainData(data)

    // 计算RMS
    let sum = 0
    for (let i = 0; i < data.length; i++) {
      sum += data[i] * data[i]
    }
    const rms = Math.sqrt(sum / data.length)

    if (rms > this.threshold) {
      if (!this.isSpeaking) {
        this.isSpeaking = true
        this.onSpeechStart()
      }
      clearTimeout(this.silenceTimer)
      this.silenceTimer = setTimeout(() => {
        this.isSpeaking = false
        this.onSpeechEnd()
      }, this.silenceDuration)
    }

    requestAnimationFrame(() => this._detect())
  }

  stop() {
    this.running = false
    clearTimeout(this.silenceTimer)
    if (this.audioContext) {
      this.audioContext.close()
    }
  }
}

// 播放音频
export function playAudio(audioData, mimeType = 'audio/mpeg') {
  const blob = new Blob([audioData], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const audio = new Audio(url)
  audio.play()
  audio.onended = () => URL.revokeObjectURL(url)
  return audio
}

// 播放base64音频
export function playBase64Audio(base64Data, mimeType = 'audio/mpeg') {
  const binaryStr = atob(base64Data)
  const bytes = new Uint8Array(binaryStr.length)
  for (let i = 0; i < binaryStr.length; i++) {
    bytes[i] = binaryStr.charCodeAt(i)
  }
  return playAudio(bytes.buffer, mimeType)
}
