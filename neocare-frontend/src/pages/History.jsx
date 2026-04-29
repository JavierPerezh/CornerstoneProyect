import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'
import { apiService } from '../api'
import './History.css'

function formatDate(isoString) {
  return new Date(isoString).toLocaleDateString('es-CO', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export default function History() {
  const [historial, setHistorial] = useState([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState(null)
  const [selectedDetails, setSelectedDetails] = useState(null)
  const { token, usuarioUuid } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    const loadHistorial = async () => {
      if (token && usuarioUuid) {
        try {
          const data = await apiService.getHistorial(usuarioUuid, token, { limit: 100 })
          setHistorial(data.items || [])
        } catch (err) {
          console.error('Error loading historial:', err)
        }
      }
      setLoading(false)
    }
    loadHistorial()
  }, [token, usuarioUuid])

  const handleSelectChat = async (chatId) => {
    try {
      const details = await apiService.getInteraccion(chatId, token)
      setSelectedDetails(details)
      setSelected(chatId)
    } catch (err) {
      console.error('Error loading interaction:', err)
    }
  }

  if (selected && selectedDetails) {
    return (
      <div className="history-layout">
        <Sidebar />
        <main className="history-main">
          <button className="history-back" onClick={() => setSelected(null)}>
            ← Volver al historial
          </button>
          <h1 className="history-chat-title">{selectedDetails.user_text?.slice(0, 60)}</h1>
          <p className="history-sub">{formatDate(selectedDetails.created_at)}</p>

          <div className="history-messages">
            <div className="hm-msg hm-msg--user">
              <div className="hm-bubble">{selectedDetails.user_text}</div>
            </div>
            <div className="hm-msg hm-msg--bot">
              <div className="hm-avatar">N</div>
              <div className="hm-bubble">{selectedDetails.assistant_text}</div>
            </div>
          </div>

          {selectedDetails.nivel_alerta && (
            <div className="history-metadata">
              <p><strong>Nivel de alerta:</strong> <span className={`alert-${selectedDetails.nivel_alerta}`}>{selectedDetails.nivel_alerta}</span></p>
              <p><strong>Riesgo:</strong> {(selectedDetails.puntuacion_riesgo * 100).toFixed(1)}%</p>
              {selectedDetails.recomendaciones && <p><strong>Recomendaciones:</strong> {selectedDetails.recomendaciones}</p>}
            </div>
          )}
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

        {loading ? (
          <div className="history-loading">Cargando historial...</div>
        ) : historial.length === 0 ? (
          <div className="history-empty">
            <span>◎</span>
            <p>Aun no tienes conversaciones guardadas.</p>
            <button className="history-cta" onClick={() => navigate('/chat')}>
              Iniciar una conversacion
            </button>
          </div>
        ) : (
          <ul className="history-list">
            {historial.map(chat => (
              <li key={chat.id} className="history-item">
                <button
                  className="history-item-btn"
                  onClick={() => handleSelectChat(chat.id)}
                >
                  <div className="history-info">
                    <p className="history-date">{formatDate(chat.created_at)}</p>
                    <p className="history-summary">{chat.user_text?.slice(0, 50)}...</p>
                    <p className="history-origin">
                      Origen: {chat.origin === 'voz' ? 'Voz' : 'Texto'}
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
