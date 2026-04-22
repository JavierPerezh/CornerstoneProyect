import { useState, useRef, useEffect } from 'react'
import './ChatWindow.css'

// ─── Helpers ──────────────────────────────────────────────────────────────────
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

function getStoredChats() {
  try {
    return JSON.parse(localStorage.getItem('neocare_chats') || '[]')
  } catch {
    return []
  }
}

function saveChats(chats) {
  localStorage.setItem('neocare_chats', JSON.stringify(chats))
}

function newChat(id) {
  return {
    id,
    title: 'Nueva conversación',
    createdAt: new Date().toISOString(),
    messages: [
      {
        id: 'welcome',
        role: 'bot',
        text: 'Hola, soy Neocare. Estoy aquí para acompañarte durante tu etapa de posparto. ¿Cómo te sientes hoy?',
        timestamp: new Date().toISOString(),
      },
    ],
  }
}

// ─── Componente principal ──────────────────────────────────────────────────────
export default function ChatWindow() {
  const [chats, setChats] = useState(() => {
    const stored = getStoredChats()
    if (stored.length === 0) {
      const initial = newChat(Date.now().toString())
      saveChats([initial])
      return [initial]
    }
    return stored
  })

  const [activeChatId, setActiveChatId] = useState(() => {
    const stored = getStoredChats()
    return stored[0]?.id ?? null
  })

  const [input, setInput] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  const activeChat = chats.find(c => c.id === activeChatId)

  // Auto-scroll al último mensaje
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [activeChat?.messages])

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 140) + 'px'
  }, [input])

  function updateChats(updater) {
    setChats(prev => {
      const updated = updater(prev)
      saveChats(updated)
      return updated
    })
  }

  function handleSend() {
    const text = input.trim()
    if (!text || !activeChatId) return

    const userMsg = {
      id: Date.now().toString(),
      role: 'user',
      text,
      timestamp: new Date().toISOString(),
    }

    // Actualiza título del chat con el primer mensaje del usuario
    updateChats(prev =>
      prev.map(c => {
        if (c.id !== activeChatId) return c
        const isFirstUserMsg = c.messages.filter(m => m.role === 'user').length === 0
        return {
          ...c,
          title: isFirstUserMsg ? text.slice(0, 40) + (text.length > 40 ? '…' : '') : c.title,
          messages: [...c.messages, userMsg],
        }
      })
    )

    setInput('')
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  function handleNewChat() {
    const chat = newChat(Date.now().toString())
    updateChats(prev => [chat, ...prev])
    setActiveChatId(chat.id)
  }

  function handleDeleteChat(id) {
    updateChats(prev => {
      const filtered = prev.filter(c => c.id !== id)
      if (filtered.length === 0) {
        const fresh = newChat(Date.now().toString())
        setActiveChatId(fresh.id)
        return [fresh]
      }
      if (id === activeChatId) setActiveChatId(filtered[0].id)
      return filtered
    })
  }

  // ─── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="cw-root">
      {/* ── Historial lateral ── */}
      <aside className={`cw-sidebar ${sidebarOpen ? '' : 'cw-sidebar--collapsed'}`}>
        <div className="cw-sidebar-header">
          <span className="cw-sidebar-title">Conversaciones</span>
          <button
            className="cw-icon-btn"
            onClick={handleNewChat}
            title="Nueva conversación"
          >
            ＋
          </button>
        </div>

        <ul className="cw-chat-list">
          {chats.map(chat => (
            <li
              key={chat.id}
              className={`cw-chat-item ${chat.id === activeChatId ? 'cw-chat-item--active' : ''}`}
            >
              <button
                className="cw-chat-item-btn"
                onClick={() => setActiveChatId(chat.id)}
              >
                <span className="cw-chat-item-title">{chat.title}</span>
                <span className="cw-chat-item-date">
                  {formatDateLabel(new Date(chat.createdAt))}
                </span>
              </button>
              <button
                className="cw-delete-btn"
                onClick={() => handleDeleteChat(chat.id)}
                title="Eliminar"
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      </aside>

      {/* ── Área de mensajes ── */}
      <div className="cw-main">
        {/* Toggle sidebar en móvil */}
        <button
          className="cw-sidebar-toggle"
          onClick={() => setSidebarOpen(o => !o)}
          title="Mostrar/ocultar historial"
        >
          ☰
        </button>

        <div className="cw-messages">
          {activeChat?.messages.map((msg, i) => {
            const showDate =
              i === 0 ||
              new Date(msg.timestamp).toDateString() !==
                new Date(activeChat.messages[i - 1].timestamp).toDateString()

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
                    <span className="cw-time">{formatTime(new Date(msg.timestamp))}</span>
                  </div>
                </div>
              </div>
            )
          })}

          <div ref={messagesEndRef} />
        </div>

        {/* ── Input ── */}
        <div className="cw-input-area">
          <textarea
            ref={textareaRef}
            className="cw-textarea"
            rows={1}
            placeholder="Escribe tu mensaje…"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            className="cw-send-btn"
            onClick={handleSend}
            disabled={!input.trim()}
            title="Enviar"
          >
            ↑
          </button>
        </div>
      </div>
    </div>
  )
}
