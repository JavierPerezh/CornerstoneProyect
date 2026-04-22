import Sidebar from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'
import './Profile.css'

export default function Profile() {
  const { user } = useAuth()

  return (
    <div className="profile-layout">
      <Sidebar />
      <main className="profile-main">
        <h1>Mi perfil</h1>
        <p className="profile-sub">Información de tu cuenta Neocare</p>

        <div className="profile-card">
          <div className="profile-avatar">
            {user?.name?.charAt(0).toUpperCase()}
          </div>
          <div className="profile-info">
            <p className="profile-name">{user?.name}</p>
            <p className="profile-email">{user?.email}</p>
          </div>
        </div>

        <div className="profile-fields">
          <div className="profile-field">
            <label>Semana posparto actual</label>
            <input type="number" defaultValue={4} min={0} max={52} />
          </div>
          <div className="profile-field">
            <label>Fecha de parto</label>
            <input type="date" />
          </div>
          <div className="profile-field">
            <label>Nombre del bebé</label>
            <input type="text" placeholder="Opcional" />
          </div>
        </div>

        <button className="save-btn">Guardar cambios</button>
      </main>
    </div>
  )
}
