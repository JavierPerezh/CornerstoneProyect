import { useState, useRef, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { apiService } from '../api'
import './ChatWindow.css'

function formatTime(date) {
  return date.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })
}

function formatDateLabel(date) {
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)

  if (date.toDateString() === today.toDateString()) return 'Hoy'
  if (date.toDateString() === yesterday.toDateString()) return 'Ayer'
  return date.toLocaleDateString('es-CO', { day: 'numeric', month: 'long' })
}

export default function ChatWindow() {
  const { token, usuarioUuid } = useAuth()
  const [historial, setHistorial] = useState([])
  const [currentMessages, setCurrentMessages] = useState([
    {
      id: 'welcome',
      role: 'bot',
      text: 'Hola, soy Neocare. Estoy aquí para acompañarte durante tu etapa de posparto. ¿Cómo te sientes hoy?',
      timestamp: new Date().toISOString(),
    },
  ])
  const [input, setInput] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [currentMessages])

  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 140) + 'px'
  }, [input])

  useEffect(() => {
    const loadHistorial = async () => {
      if (token && usuarioUuid) {
        try {
          const data = await apiService.getHistorial(usuarioUuid, token, { limit: 50 })
          setHistorial(data.items || [])
        } catch (err) {
          console.error('Error loading historial:', err)
        }
      }
    }
    loadHistorial()
  }, [token, usuarioUuid])

  const handleSend = async () => {
    const text = input.trim()
    if (!text || !token || !usuarioUuid || loading) return

    const userMsg = {
      id: Date.now().toString(),
      role: 'user',
      text,
      timestamp: new Date().toISOString(),
    }

    setCurrentMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const response = await apiService.sendMessage(text, usuarioUuid, token)
      
      const botMsg = {
        id: response.interaccion_id?.toString() || Date.now().toString(),
        role: 'bot',
        text: response.respuesta,
        timestamp: new Date().toISOString(),
        metadata: {
          nivel_alerta: response.nivel_alerta,
          puntuacion_riesgo: response.puntuacion_riesgo,
          requiere_accion_inmediata: response.requiere_accion_inmediata,
          recomendaciones: response.recomendaciones,
        },
      }
      
      setCurrentMessages(prev => [...prev, botMsg])
    } catch (err) {
      const errorMsg = {
        id: Date.now().toString(),
        role: 'bot',
        text: 'Lo siento, hubo un error al procesar tu mensaje. Por favor intenta de nuevo.',
        timestamp: new Date().toISOString(),
      }
      setCurrentMessages(prev => [...prev, errorMsg])
      console.error('Error sending message:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="cw-root">
      <aside className={`cw-sidebar ${sidebarOpen ? '' : 'cw-sidebar--collapsed'}`}>
        <div className="cw-sidebar-header">
          <span className="cw-sidebar-title">Conversaciones</span>
        </div>

        <ul className="cw-chat-list">
          {historial.length === 0 ? (
            <li className="cw-chat-item-empty">Sin conversaciones previas</li>
          ) : (
            historial.slice().reverse().map(chat => (
              <li key={chat.id} className="cw-chat-item">
                <button className="cw-chat-item-btn">
                  <span className="cw-chat-item-title">{chat.user_text?.slice(0, 40)}...</span>
                  <span className="cw-chat-item-date">
                    {formatDateLabel(new Date(chat.created_at))}
                  </span>
                </button>
              </li>
            ))
          )}
        </ul>
      </aside>

      <div className="cw-main">
        <button
          className="cw-sidebar-toggle"
          onClick={() => setSidebarOpen(o => !o)}
          title="Mostrar/ocultar historial"
        >
          ☰
        </button>

        <div className="cw-messages">
          {currentMessages.map((msg, i) => {
            const showDate =
              i === 0 ||
              new Date(msg.timestamp).toDateString() !==
                new Date(currentMessages[i - 1].timestamp).toDateString()

            return (
              <div key={msg.id}>
                {showDate && (
                  <div className="cw-date-divider">
                    <span>{formatDateLabel(new Date(msg.timestamp))}</span>
                  </div>
                )}
                <div className={`cw-msg cw-msg--${msg.role}`}>
                  {msg.role === 'bot' && (
                    <div className="cw-avatar">N</div>
                  )}
                  <div className="cw-bubble-wrap">
                    <div className="cw-bubble">{msg.text}</div>
                    {msg.metadata?.nivel_alerta && (
                      <div className="cw-metadata">
                        <span className={`alert-badge alert-${msg.metadata.nivel_alerta}`}>
                          {msg.metadata.nivel_alerta.toUpperCase()}
                        </span>
                      </div>
                    )}
                    <span className="cw-time">{formatTime(new Date(msg.timestamp))}</span>
                  </div>
                </div>
              </div>
            )
          })}
          {loading && (
            <div className="cw-msg cw-msg--bot">
              <div className="cw-avatar">N</div>
              <div className="cw-bubble-wrap">
                <div className="cw-bubble cw-bubble--loading">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="cw-input-area">
          <textarea
            ref={textareaRef}
            className="cw-textarea"
            rows={1}
            placeholder="Escribe tu mensaje…"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            className="cw-send-btn"
            onClick={handleSend}
            disabled={!input.trim() || loading}
            title="Enviar"
          >
            ↑
          </button>
        </div>
      </div>
    </div>
  )
}
