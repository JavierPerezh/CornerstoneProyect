import { useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Sidebar from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'
import { apiService } from '../api'
import './Dashboard.css'

const TIPS = [
  'Recuerda hidratarte bien durante la lactancia.',
  'Si sientes tristeza persistente por mas de 2 semanas, consulta a tu médico.',
  'Intenta descansar cuando tu bebé duerma.',
]

export default function Dashboard() {
  const { nombre, weeksPostpartum, token, usuarioUuid } = useAuth()
  const [progreso, setProgreso] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchProgreso = async () => {
      if (token && usuarioUuid) {
        try {
          const data = await apiService.getProgresoResumen(usuarioUuid, token, 'semana')
          setProgreso(data)
        } catch (err) {
          console.error('Error fetching progreso:', err)
        }
      }
      setLoading(false)
    }
    fetchProgreso()
  }, [token, usuarioUuid])

  const STATS = [
    {
      label: 'Semana posparto',
      value: weeksPostpartum !== null ? String(weeksPostpartum) : '—',
      unit: weeksPostpartum !== null ? 'sem' : '',
    },
    { label: 'Conversaciones', value: String(progreso?.total_interacciones || 0), unit: 'total' },
    { label: 'Nivel de riesgo', value: determineRiskLevel(progreso?.riesgo_promedio), unit: '' },
    { label: 'Alertas rojas', value: String(progreso?.alertas?.rojo || 0), unit: 'critico' },
  ]

  function determineRiskLevel(averageRisk) {
    if (!averageRisk) return 'Verde'
    if (averageRisk < 0.33) return 'Verde'
    if (averageRisk < 0.66) return 'Amarillo'
    return 'Rojo'
  }

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <main className="dashboard-main">
        <header className="dash-header">
          <div>
            <h1>Hola, {nombre}</h1>
            <p className="dash-sub">¿Cómo te sientes hoy?</p>
          </div>
        </header>

        <button className="chat-cta" onClick={() => navigate('/chat')}>
          <div className="cta-icon">◎</div>
          <div>
            <p className="cta-title">Hablar con Neocare</p>
            <p className="cta-desc">Tu acompañante de posparto está lista para escucharte</p>
          </div>
          <span className="cta-arrow">→</span>
        </button>

        <section className="stats-grid">
          {STATS.map(({ label, value, unit }) => (
            <div key={label} className="stat-card">
              <p className="stat-label">{label}</p>
              <p className="stat-value">
                {value}
                {unit && <span className="stat-unit"> {unit}</span>}
              </p>
            </div>
          ))}
        </section>

        {progreso && (
          <section className="symptoms-section">
            <h2>Síntomas frecuentes (esta semana)</h2>
            {progreso.sintomas_madre_frecuentes && progreso.sintomas_madre_frecuentes.length > 0 && (
              <div className="symptoms-list">
                <h3>Madre:</h3>
                <ul>
                  {progreso.sintomas_madre_frecuentes.slice(0, 3).map((s, i) => (
                    <li key={i}>{s.sintoma} ({s.frecuencia}x)</li>
                  ))}
                </ul>
              </div>
            )}
            {progreso.sintomas_bebe_frecuentes && progreso.sintomas_bebe_frecuentes.length > 0 && (
              <div className="symptoms-list">
                <h3>Bebé:</h3>
                <ul>
                  {progreso.sintomas_bebe_frecuentes.slice(0, 3).map((s, i) => (
                    <li key={i}>{s.sintoma} ({s.frecuencia}x)</li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}

        <section className="tips-section">
          <h2>Consejos del día</h2>
          <ul className="tips-list">
            {TIPS.map((tip, i) => (
              <li key={i} className="tip-item">
                <span className="tip-dot" />
                {tip}
              </li>
            ))}
          </ul>
        </section>
      </main>
    </div>
  )
}
