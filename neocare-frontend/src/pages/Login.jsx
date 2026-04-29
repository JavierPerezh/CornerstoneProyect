import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import logo from '../assets/logo_neocare.png'
import flor1 from '../assets/flor1.png'
import flor2 from '../assets/flor2.png'
import flor3 from '../assets/flor3.png'
import './Login.css'

export default function Login() {
  const [tab, setTab] = useState('login')

  // Login
  const [loginEmail, setLoginEmail] = useState('')
  const [loginPassword, setLoginPassword] = useState('')

  // Signup
  const [signupName, setSignupName] = useState('')
  const [signupEmail, setSignupEmail] = useState('')
  const [signupPassword, setSignupPassword] = useState('')
  const [babyBirthdate, setBabyBirthdate] = useState('')

  const [error, setError] = useState('')

  const { login, signup } = useAuth()
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    const ok = await login(loginEmail, loginPassword)
    if (ok) navigate('/')
    else setError('Correo o contraseña incorrectos')
  }

  const handleSignup = async (e) => {
    e.preventDefault()
    setError('')
    if (!babyBirthdate) {
      setError('Por favor ingresa la fecha de nacimiento de tu bebe')
      return
    }
    const ok = await signup(signupName, signupEmail, signupPassword, babyBirthdate)
    if (ok) navigate('/')
    else setError('Completa todos los campos para continuar')
  }

  // Fecha maxima: hoy. Fecha minima: 12 meses atras (fuera del posparto)
  const today = new Date().toISOString().split('T')[0]
  const minDate = new Date()
  minDate.setFullYear(minDate.getFullYear() - 1)
  const minDateStr = minDate.toISOString().split('T')[0]

  return (
    <div className="login-page">
      <div className="login-left">
        <div className="login-brand">
          <img src={logo} alt="Neocare" className="login-logo" />
          <span className="brand-name"><strong>NEOCARE</strong></span>
        </div>
        <p className="login-tagline">
          Acompanamiento médico y emocional para madres en posparto.
        </p>
        <div className="login-deco" aria-hidden>
          <img src={flor1} className="deco-flor f1" alt="" />
          <img src={flor2} className="deco-flor f2" alt="" />
          <img src={flor3} className="deco-flor f3" alt="" />
        </div>
      </div>

      <div className="login-right">
        <div className="login-card">
          <div className="login-tabs">
            <button
              className={`tab-btn ${tab === 'login' ? 'tab-btn--active' : ''}`}
              onClick={() => { setTab('login'); setError('') }}
            >
              Iniciar sesión
            </button>
            <button
              className={`tab-btn ${tab === 'signup' ? 'tab-btn--active' : ''}`}
              onClick={() => { setTab('signup'); setError('') }}
            >
              Registrarse
            </button>
          </div>

          {tab === 'login' ? (
            <form className="login-form" onSubmit={handleLogin}>
              <div className="field">
                <label>Correo electrónico</label>
                <input
                  type="email"
                  placeholder="tu@correo.com"
                  value={loginEmail}
                  onChange={e => setLoginEmail(e.target.value)}
                  required
                />
              </div>
              <div className="field">
                <label>Contraseña</label>
                <input
                  type="password"
                  placeholder="Contraseña"
                  value={loginPassword}
                  onChange={e => setLoginPassword(e.target.value)}
                  required
                />
              </div>
              {error && <p className="login-error">{error}</p>}
              <button type="submit" className="login-submit">Entrar</button>
            </form>
          ) : (
            <form className="login-form" onSubmit={handleSignup}>
              <div className="field">
                <label>Nombre completo</label>
                <input
                  type="text"
                  placeholder="Tu nombre"
                  value={signupName}
                  onChange={e => setSignupName(e.target.value)}
                  required
                />
              </div>
              <div className="field">
                <label>Correo electrónico</label>
                <input
                  type="email"
                  placeholder="tu@correo.com"
                  value={signupEmail}
                  onChange={e => setSignupEmail(e.target.value)}
                  required
                />
              </div>
              <div className="field">
                <label>Contraseña</label>
                <input
                  type="password"
                  placeholder="Contraseña"
                  value={signupPassword}
                  onChange={e => setSignupPassword(e.target.value)}
                  required
                />
              </div>
              <div className="field">
                <label>Fecha de nacimiento de tu bebe</label>
                <input
                  type="date"
                  value={babyBirthdate}
                  onChange={e => setBabyBirthdate(e.target.value)}
                  min={minDateStr}
                  max={today}
                  required
                />
                <span className="field-hint">
                  Usamos esta fecha para calcular tus semanas de posparto
                </span>
              </div>
              {error && <p className="login-error">{error}</p>}
              <button type="submit" className="login-submit">Crear cuenta</button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
