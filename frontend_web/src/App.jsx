import { useState } from "react";
import logo_neocare from "./assets/logo_neocare.png";

function App() {
  const [mensajes, setMensajes] = useState([]);
  const [texto, setTexto] = useState("");

  const enviarMensaje = () => {
    if (texto.trim() === "") return;

    setMensajes([...mensajes, texto]);
    setTexto("");
  };

  return (
    <div style={{ padding: "20px" }}>
      <img src={logo_neocare} alt="logo_neocare" style={{ width: "70px", display: "flex", justifyContent: "flex-start" }} />
      <h1 style={{ color: "#bda182", fontFamily: "Bricolage Grotesque"}}>Neocare</h1>

      <div style={{ border: "3px solid #bda182", height: "300px", padding: "10px", overflowY: "auto" }}>
        {mensajes.map((msg, index) => (
          <div key={index} style={{display: "flex", justifyContent: "flex-end"}}>
            <div
              style={{ backgroundColor: "#fce7f3", padding: "8px 12px", borderRadius: "10px", margin: "5px 0", maxWidth: "70%"}}
            >{msg}

            </div>

          </div>
        ))}
      </div>

      <div style={{ marginTop: "10px" }}>
        <input
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              enviarMensaje();
            }
          }}

          placeholder="Escribe un mensaje..."
          style={{ padding: "5px", fontFamily: "Bricolage Grotesque", width: "70%" }}
        />

        <button onClick={enviarMensaje} style={{ marginLeft: "10px", borderColor: "white", backgroundColor: "#f0e084", fontFamily: "Bricolage Grotesque", color: "#312108" }}>
          Enviar
        </button>
      </div>
    </div>
  );
}

export default App;
