// Sentio-AI Auth Composable
// Author: shuhuNB560 / shuhuNB515
import { reactive } from 'vue'
import { authAPI, conversationAPI } from '../api'

const state = reactive({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('token') || null,
  currentConversationId: null,
  conversations: [],
  isLoggedIn: !!localStorage.getItem('token'),
})

export function useAuth() {
  const login = async (username, password) => {
    const res = await authAPI.login(username, password)
    state.token = res.data.token
    state.user = res.data.user
    state.isLoggedIn = true
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    await loadConversations()
  }

  const register = async (username, password) => {
    const res = await authAPI.register(username, password)
    state.token = res.data.token
    state.user = res.data.user
    state.isLoggedIn = true
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
  }

  const logout = () => {
    state.token = null
    state.user = null
    state.isLoggedIn = false
    state.currentConversationId = null
    state.conversations = []
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const loadConversations = async () => {
    if (!state.isLoggedIn) return
    try {
      const res = await conversationAPI.list()
      state.conversations = res.data
    } catch (e) {
      console.error('Failed to load conversations', e)
    }
  }

  const createConversation = async (title = 'New Conversation') => {
    const res = await conversationAPI.create(title)
    state.currentConversationId = res.data.id
    await loadConversations()
    return res.data.id
  }

  const setCurrentConversation = (id) => {
    state.currentConversationId = id
  }

  const deleteConversation = async (id) => {
    await conversationAPI.delete(id)
    if (state.currentConversationId === id) {
      state.currentConversationId = null
    }
    await loadConversations()
  }

  return {
    state,
    login,
    register,
    logout,
    loadConversations,
    createConversation,
    setCurrentConversation,
    deleteConversation,
  }
}
