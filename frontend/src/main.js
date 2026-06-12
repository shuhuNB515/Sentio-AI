import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import LoginPage from './views/LoginPage.vue'
import MainPage from './views/MainPage.vue'

// Sentio-AI by shuhuNB560 / shuhuNB515
console.log('%c Sentio-AI %c by shuhuNB560 ',
  'background:#6366f1;color:white;padding:4px 8px;border-radius:4px 0 0 4px;font-weight:bold',
  'background:#312e81;color:#a5b4fc;padding:4px 8px;border-radius:0 4px 4px 0')

const routes = [
  { path: '/login', component: LoginPage, meta: { guest: true } },
  { path: '/', component: MainPage, meta: { auth: true } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.auth && !token) {
    next('/login')
  } else if (to.meta.guest && token) {
    next('/')
  } else {
    next()
  }
})

const app = createApp(App)
app.use(router)
app.mount('#app')
