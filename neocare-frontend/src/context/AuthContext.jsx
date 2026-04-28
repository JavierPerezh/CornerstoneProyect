import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

function calcWeeksPostpartum(babyBirthdate) {
  if (!babyBirthdate) return null
  const birth = new Date(babyBirthdate)
  const now = new Date()
  const diffMs = now - birth
  const weeks = Math.floor(diffMs / (1000 * 60 * 60 * 24 * 7))
  return weeks >= 0 ? weeks : null
}

function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem('neocare_user') || 'null')
  } catch { return null }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getStoredUser())

  const login = (email, password) => {
    if (email && password) {
      const stored = getStoredUser()
      if (stored && stored.email === email) {
        setUser(stored)
        return true
      }
      const newUser = { name: email.split('@')[0], email, babyBirthdate: null }
      localStorage.setItem('neocare_user', JSON.stringify(newUser))
      setUser(newUser)
      return true
    }
    return false
  }

  const signup = (name, email, password, babyBirthdate) => {
    if (name && email && password && babyBirthdate) {
      const newUser = { name, email, babyBirthdate }
      localStorage.setItem('neocare_user', JSON.stringify(newUser))
      setUser(newUser)
      return true
    }
    return false
  }

  const logout = () => {
    localStorage.removeItem('neocare_user')
    setUser(null)
  }

  const chatCount = () => {
    try {
      const chats = JSON.parse(localStorage.getItem('neocare_chats') || '[]')
      return chats.length
    } catch { return 0 }
  }

  const weeksPostpartum = user?.babyBirthdate
    ? calcWeeksPostpartum(user.babyBirthdate)
    : null

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, chatCount, weeksPostpartum }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
