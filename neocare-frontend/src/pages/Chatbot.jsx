import Sidebar from '../components/Sidebar'
import ChatWindow from '../components/ChatWindow'
import './Chatbot.css'

export default function Chatbot() {
  return (
    <div className="chatbot-layout">
      <Sidebar />
      <main className="chatbot-main">
        <div className="chatbot-header">
          <div className="bot-avatar">N</div>
          <div>
            <h1>Neocare</h1>
            <span className="bot-status">● En línea</span>
          </div>
        </div>

        <div className="chatbot-frame">
          <ChatWindow />
        </div>
      </main>
    </div>
  )
}
