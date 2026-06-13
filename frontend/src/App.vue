<template>
  <router-view />
</template>

<script setup>
</script>

<style>
/* Sentio-AI by shuhuNB560 / shuhuNB515 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --bg-primary: rgba(30, 10, 50, 0.55);
  --bg-secondary: rgba(35, 12, 55, 0.5);
  --bg-tertiary: rgba(45, 15, 70, 0.45);
  --bg-card: rgba(50, 18, 80, 0.4);
  --bg-hover: rgba(60, 22, 95, 0.5);
  --border-primary: rgba(139, 92, 246, 0.35);
  --border-glow: #a78bfa;
  --text-primary: #e8e8f0;
  --text-secondary: #c4b5fd;
  --text-muted: #a78bfa;
  --accent-primary: #a78bfa;
  --accent-secondary: #c084fc;
  --accent-gradient: linear-gradient(135deg, #8b5cf6, #a78bfa, #c4b5fd);
  --accent-glow: rgba(167, 139, 250, 0.35);
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --info: #06b6d4;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --shadow-sm: 0 2px 8px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.4);
  --shadow-lg: 0 8px 32px rgba(0,0,0,0.5);
  --shadow-glow: 0 0 20px var(--accent-glow);
  --transition: all 0.2s ease;
}

html, body, #app {
  width: 100%;
  height: 100%;
  overflow: hidden;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
}

::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: var(--border-primary);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

input, button, textarea {
  font-family: inherit;
}

a {
  color: var(--accent-primary);
  text-decoration: none;
}
</style>
