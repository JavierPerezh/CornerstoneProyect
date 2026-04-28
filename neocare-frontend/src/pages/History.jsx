import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import './History.css'

function formatDate(isoString) {
  return new Date(isoString).toLocaleDateString('es-CO', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function getStoredChats() {
  try {
    return JSON.parse(localStorage.getItem('neocare_chats') || '[]')
  } catch { return [] }
}

export default function History() {
  const [chats, setChats] = useState([])
  const [selected, setSelected] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    setChats(getStoredChats())
  }, [])

  if (selected) {
    const chat = chats.find(c => c.id === selected)
    return (
      <div className="history-layout">
        <Sidebar />
        <main className="history-main">
          <button className="history-back" onClick={() => setSelected(null)}>
            ← Volver al historial
          </button>
          <h1 className="history-chat-title">{chat.title}</h1>
          <p className="history-sub">{formatDate(chat.createdAt)}</p>

          <div className="history-messages">
            {chat.messages.map(msg => (
              <div key={msg.id} className={`hm-msg hm-msg--${msg.role}`}>
                {msg.role === 'bot' && <div className="hm-avatar">N</div>}
                <div className="hm-bubble">{msg.text}</div>
              </div>
            ))}
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="history-layout">
      <Sidebar />
      <main className="history-main">
        <h1>Historial de conversaciones</h1>
        <p className="history-sub">Registro de tus sesiones con Neocare</p>

        {chats.length === 0 ? (
          <div className="history-empty">
            <span>◎</span>
            <p>Aun no tienes conversaciones guardadas.</p>
            <button className="history-cta" onClick={() => navigate('/chat')}>
              Iniciar una conversacion
            </button>
          </div>
        ) : (
          <ul className="history-list">
            {chats.map(chat => (
              <li key={chat.id} className="history-item">
                <button
                  className="history-item-btn"
                  onClick={() => setSelected(chat.id)}
                >
                  <div className="history-info">
                    <p className="history-date">{formatDate(chat.createdAt)}</p>
                    <p className="history-summary">{chat.title}</p>
                    <p className="history-count">
                      {chat.messages.filter(m => m.role === 'user').length} mensajes tuyos
                    </p>
                  </div>
                  <span className="history-arrow">→</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  )
}
