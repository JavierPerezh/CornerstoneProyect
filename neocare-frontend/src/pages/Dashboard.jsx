import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'
import './Dashboard.css'

const TIPS = [
  'Recuerda hidratarte bien durante la lactancia.',
  'Si sientes tristeza persistente por mas de 2 semanas, consulta a tu médico.',
  'Intenta descansar cuando tu bebé duerma.',
]

export default function Dashboard() {
  const { user, chatCount, weeksPostpartum } = useAuth()
  const navigate = useNavigate()

  const STATS = [
    {
      label: 'Semana posparto',
      value: weeksPostpartum !== null ? String(weeksPostpartum) : '—',
      unit: weeksPostpartum !== null ? 'sem' : '',
    },
    { label: 'Conversaciones', value: String(chatCount()), unit: 'total' },
    { label: 'Nivel de riesgo',  value: 'Verde', unit: '' },
    { label: 'Última sesión',    value: 'Hoy',   unit: '' },
  ]

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <main className="dashboard-main">
        <header className="dash-header">
          <div>
            <h1>Hola, {user?.name}</h1>
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
