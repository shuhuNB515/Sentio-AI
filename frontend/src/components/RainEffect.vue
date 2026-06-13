<template>
  <div class="rain-container" ref="container">
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const container = ref(null)
const canvas = ref(null)
let ctx = null
let animId = null
let W = 0, H = 0

// 雨滴
const drops = []
const MAX_DROPS = 80

// 涟漪（双重圆形）
const ripples = []

// 五角星涟漪
const starRipples = []

class RainDrop {
  constructor() {
    this.reset()
  }
  reset() {
    // 从左上往右下，x起始偏左，y起始偏上
    this.x = Math.random() * W * 1.2 - W * 0.1
    this.y = -Math.random() * H * 0.3 - 20
    this.speed = 2 + Math.random() * 4
    this.length = 15 + Math.random() * 25
    this.opacity = 0.15 + Math.random() * 0.35
    this.wind = 0.8 + Math.random() * 1.5 // 向右的风力
    this.thickness = 0.8 + Math.random() * 1.2
  }
  update() {
    this.y += this.speed
    this.x += this.wind
    if (this.y > H) {
      // 到达底部，生成涟漪
      if (Math.random() < 0.4) {
        ripples.push(new Ripple(this.x, H - 2 + Math.random() * 4))
      }
      if (Math.random() < 0.25) {
        starRipples.push(new StarRipple(this.x, H - 2 + Math.random() * 4))
      }
      this.reset()
    }
  }
  draw() {
    const endX = this.x + this.wind * (this.length / this.speed)
    const endY = this.y + this.length
    ctx.beginPath()
    ctx.moveTo(this.x, this.y)
    ctx.lineTo(endX, endY)
    ctx.strokeStyle = `rgba(180, 210, 255, ${this.opacity})`
    ctx.lineWidth = this.thickness
    ctx.lineCap = 'round'
    ctx.stroke()
  }
}

class Ripple {
  constructor(x, y) {
    this.x = x
    this.y = y
    this.radius1 = 0
    this.radius2 = 0
    this.maxRadius1 = 15 + Math.random() * 20
    this.maxRadius2 = this.maxRadius1 * 0.6
    this.opacity = 0.7
    this.speed1 = 0.6 + Math.random() * 0.4
    this.speed2 = 0.4 + Math.random() * 0.3
    this.delay2 = 6 // 第二个圆延迟帧数
    this.frame = 0
    this.alive = true
  }
  update() {
    this.frame++
    if (this.radius1 < this.maxRadius1) {
      this.radius1 += this.speed1
    }
    if (this.frame > this.delay2 && this.radius2 < this.maxRadius2) {
      this.radius2 += this.speed2
    }
    this.opacity -= 0.012
    if (this.opacity <= 0) {
      this.alive = false
    }
  }
  draw() {
    // 外圆
    if (this.radius1 > 0) {
      ctx.beginPath()
      ctx.ellipse(this.x, this.y, this.radius1, this.radius1 * 0.35, 0, 0, Math.PI * 2)
      ctx.strokeStyle = `rgba(160, 200, 255, ${this.opacity})`
      ctx.lineWidth = 1.2
      ctx.stroke()
    }
    // 内圆
    if (this.radius2 > 0) {
      ctx.beginPath()
      ctx.ellipse(this.x, this.y, this.radius2, this.radius2 * 0.35, 0, 0, Math.PI * 2)
      ctx.strokeStyle = `rgba(140, 190, 255, ${this.opacity * 0.7})`
      ctx.lineWidth = 0.8
      ctx.stroke()
    }
  }
}

class StarRipple {
  constructor(x, y) {
    this.x = x
    this.y = y
    this.radius = 0
    this.maxRadius = 12 + Math.random() * 18
    this.opacity = 0.6
    this.speed = 0.4 + Math.random() * 0.3
    this.rotation = Math.random() * Math.PI * 2
    this.rotSpeed = (Math.random() - 0.5) * 0.02
    this.alive = true
    this.sides = 5 // 五角形
  }
  update() {
    if (this.radius < this.maxRadius) {
      this.radius += this.speed
    }
    this.rotation += this.rotSpeed
    this.opacity -= 0.01
    if (this.opacity <= 0) {
      this.alive = false
    }
  }
  draw() {
    if (this.radius <= 0) return
    ctx.save()
    ctx.translate(this.x, this.y)
    ctx.rotate(this.rotation)
    ctx.scale(1, 0.35) // 透视压缩

    // 画五角星
    ctx.beginPath()
    for (let i = 0; i < this.sides * 2; i++) {
      const r = i % 2 === 0 ? this.radius : this.radius * 0.45
      const angle = (Math.PI / this.sides) * i - Math.PI / 2
      const px = Math.cos(angle) * r
      const py = Math.sin(angle) * r
      if (i === 0) ctx.moveTo(px, py)
      else ctx.lineTo(px, py)
    }
    ctx.closePath()
    ctx.strokeStyle = `rgba(160, 200, 255, ${this.opacity})`
    ctx.lineWidth = 1
    ctx.stroke()

    // 内部小五角星
    if (this.radius > 5) {
      ctx.beginPath()
      const innerR = this.radius * 0.5
      for (let i = 0; i < this.sides * 2; i++) {
        const r = i % 2 === 0 ? innerR : innerR * 0.45
        const angle = (Math.PI / this.sides) * i - Math.PI / 2
        const px = Math.cos(angle) * r
        const py = Math.sin(angle) * r
        if (i === 0) ctx.moveTo(px, py)
        else ctx.lineTo(px, py)
      }
      ctx.closePath()
      ctx.strokeStyle = `rgba(140, 190, 255, ${this.opacity * 0.5})`
      ctx.lineWidth = 0.6
      ctx.stroke()
    }

    ctx.restore()
  }
}

const resize = () => {
  if (!container.value || !canvas.value) return
  W = container.value.offsetWidth
  H = container.value.offsetHeight
  canvas.value.width = W
  canvas.value.height = H
}

const init = () => {
  if (!canvas.value) return
  ctx = canvas.value.getContext('2d')
  resize()
  for (let i = 0; i < MAX_DROPS; i++) {
    const drop = new RainDrop()
    drop.y = Math.random() * H // 初始分散
    drops.push(drop)
  }
}

const animate = () => {
  if (!ctx) return
  ctx.clearRect(0, 0, W, H)

  // 更新和绘制雨滴
  for (const drop of drops) {
    drop.update()
    drop.draw()
  }

  // 更新和绘制圆形涟漪
  for (let i = ripples.length - 1; i >= 0; i--) {
    ripples[i].update()
    ripples[i].draw()
    if (!ripples[i].alive) ripples.splice(i, 1)
  }

  // 更新和绘制五角星涟漪
  for (let i = starRipples.length - 1; i >= 0; i--) {
    starRipples[i].update()
    starRipples[i].draw()
    if (!starRipples[i].alive) starRipples.splice(i, 1)
  }

  animId = requestAnimationFrame(animate)
}

onMounted(() => {
  init()
  animate()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  if (animId) cancelAnimationFrame(animId)
  window.removeEventListener('resize', resize)
})
</script>

<style scoped>
.rain-container {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 1;
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
