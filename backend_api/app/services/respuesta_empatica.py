from groq import Groq
from app.core.config import Settings

class RespuestaEmpaticaService:
    """
    Servicio encargado de generar respuestas textuales calidas y empaticas 
    utilizando modelos de lenguaje de gran escala (LLM). 
    Se integra la logica clinica con un enfoque humanizado.
    """

    def __init__(self):
        # Inicializacion del cliente con la API Key centralizada
        self.client = Groq(api_key=Settings.GROQ_API_KEY)
        # Seleccion de un modelo de ultima generacion para mayor precision linguistica
        self.model = "llama-3.3-70b-versatile" 

    def generar_respuesta(self, texto_usuario, nivel_alerta, recomendacion_medica, puntuacion_riesgo):
        """
        Construye una respuesta breve y humana basada en el contexto clinico detectado.
        
        Args:
            texto_usuario (str): Lo que la madre expreso originalmente.
            nivel_alerta (str): 'verde', 'amarillo' o 'rojo' segun el motor de reglas.
            recomendacion_medica (str): Instruccion técnica del motor de reglas.
            puntuacion_riesgo (float): Valor probabilistico del modelo de regresion.
        """
        
        # Definicion del comportamiento y personalidad del sistema (System Prompt)
        system_prompt = (
            "Eres un acompanante de posparto directo, comprensivo y experto. Comunica con emojis relevantes y estructura clara.\n\n"
            "Reglas estrictas:\n"
            "1. Idioma: Español.\n"
            "2. Extensión: 100-150 palabras máximo.\n"
            "3. Tono: Amable pero directo, sin exceso de calidez. Sé práctico.\n"
            "4. Formato: Usa emojis (3-5) y crea listas con viñetas cuando sea apropiado. Nada de párrafos largos.\n"
            "5. Estructura típica:\n"
            "   • Línea de validación breve con emoji\n"
            "   • Puntos clave en formato lista\n"
            "   • Recomendación médica directa\n"
            "   • Siguiente paso claro\n"
            "6. Incluye siempre la recomendación médica de forma accesible y directa.\n"
            "7. Si el nivel es rojo: sé claro sin alarmar, presenta urgencia sin pánico.\n"
            "8. Usa emojis para mejorar legibilidad: etc.\n"
            "9. Si hay duda, valida brevemente y recomienda consulta profesional de inmediato."
        )

        # Inyeccion de contexto clinico para guiar la generacion (User Prompt)
        prompt_usuario = (
            f"Contexto: '{texto_usuario}'\n"
            f"Alerta: {nivel_alerta.upper()} | Riesgo: {puntuacion_riesgo:.2f}\n"
            f"Recomendación: {recomendacion_medica}\n\n"
            "Genera una respuesta corta (100-150 palabras) con:\n"
            "• Validación breve con emoji\n"
            "• 2-3 puntos clave en lista\n"
            "• Recomendación médica clara\n"
            "• Próximo paso específico\n"
            "• Emojis útiles dispersos\n\n"
            "Sé directo y práctico. Nada de párrafos largos."
        )

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_usuario}
                ],
                model=self.model,
                temperature=0.6,  # Balance entre creatividad y precisión
                max_tokens=300    # Suficiente para 100-150 palabras con emojis y listas
            )
            
            return chat_completion.choices[0].message.content.strip()

        except Exception as e:
            # Mecanismo de contingencia en caso de fallo en la API externa
            print(f"Error en la generacion de respuesta LLM: {e}")
            return (
                "💙 Entiendo lo que sientes.\n\n"
                f"✅ Lo importante ahora: {recomendacion_medica}\n\n"
                "📞 Si las cosas empeoran, contacta a tu profesional de salud de inmediato.\n\n"
                "Estoy aquí para apoyarte. ¡Vamos paso a paso!"
            )

# Instancia para uso global en el backend
respuesta_service = RespuestaEmpaticaService()