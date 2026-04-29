import { createContext, useContext, useState, useEffect } from 'react'
import { apiService } from '../api'

const AuthContext = createContext(null)

function calcWeeksPostpartum(babyBirthdate) {
  if (!babyBirthdate) return null
  const birth = new Date(babyBirthdate)
  const now = new Date()
  const diffMs = now - birth
  const weeks = Math.floor(diffMs / (1000 * 60 * 60 * 24 * 7))
  return weeks >= 0 ? weeks : null
}

function getStoredAuth() {
  try {
    return JSON.parse(localStorage.getItem('neocare_auth') || 'null')
  } catch { return null }
}

function saveAuth(auth) {
  localStorage.setItem('neocare_auth', JSON.stringify(auth))
}

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => getStoredAuth())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const validateStoredToken = async () => {
      const stored = getStoredAuth()
      if (stored?.access_token) {
        try {
          await apiService.validateToken(stored.access_token)
        } catch (err) {
          setAuth(null)
          localStorage.removeItem('neocare_auth')
        }
      }
      setLoading(false)
    }
    validateStoredToken()
  }, [])

  const login = async (email, password) => {
    setError(null)
    try {
      const response = await apiService.login(email, password)
      const authData = {
        access_token: response.access_token,
        usuario_uuid: response.usuario_uuid,
        email,
      }
      saveAuth(authData)
      setAuth(authData)
      return true
    } catch (err) {
      setError(err.message)
      return false
    }
  }

  const signup = async (name, email, password, babyBirthdate) => {
    setError(null)
    try {
      const response = await apiService.register(email, password, name, babyBirthdate)
      const authData = {
        access_token: response.access_token,
        usuario_uuid: response.usuario_uuid,
        email,
        nombre: name,
        babyBirthdate,
      }
      saveAuth(authData)
      setAuth(authData)
      return true
    } catch (err) {
      setError(err.message)
      return false
    }
  }

  const logout = () => {
    localStorage.removeItem('neocare_auth')
    setAuth(null)
  }

  const weeksPostpartum = auth?.babyBirthdate
    ? calcWeeksPostpartum(auth.babyBirthdate)
    : null

  const isAuthenticated = !!auth?.access_token
  const token = auth?.access_token
  const usuarioUuid = auth?.usuario_uuid
  const nombre = auth?.nombre || auth?.email?.split('@')[0]

  return (
    <AuthContext.Provider value={{
      auth,
      isAuthenticated,
      token,
      usuarioUuid,
      nombre,
      loading,
      error,
      login,
      signup,
      logout,
      weeksPostpartum,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
