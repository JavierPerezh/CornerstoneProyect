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
            "Eres un acompanante de posparto empatico y experto. Tu objetivo es validar "
            "las emociones de la madre y dar instrucciones claras basadas en medicina. "
            "Reglas estrictas:\n"
            "1. Idioma: Espanol.\n"
            "2. Extension: Maximo 280 caracteres (prioriza la brevedad para TTS).\n"
            "3. Tono: Calido, calmado y sin juicios.\n"
            "4. Estructura: Valida la emocion, explica brevemente el riesgo y da el paso a seguir."
        )

        # Inyeccion de contexto clinico para guiar la generacion (User Prompt)
        prompt_usuario = (
            f"Contexto de la madre: '{texto_usuario}'\n"
            f"Evaluacion tecnica: Nivel de alerta {nivel_alerta.upper()}.\n"
            f"Puntuacion de riesgo logistico: {puntuacion_riesgo:.2f}.\n"
            f"Instruccion medica: {recomendacion_medica}\n\n"
            "Genera la respuesta directa para la madre:"
        )

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_usuario}
                ],
                model=self.model,
                temperature=0.5, # Balance entre creatividad y precision
                max_tokens=150   # Garantiza que la respuesta sea procesable por el TTS
            )
            
            return chat_completion.choices[0].message.content.strip()

        except Exception as e:
            # Mecanismo de contingencia en caso de fallo en la API externa
            print(f"Error en la generacion de respuesta LLM: {e}")
            return (
                "Entiendo como te sientes. Segun lo que me cuentas, lo mas importante es: "
                f"{recomendacion_medica}. Estoy aqui para acompanarte."
            )

# Instancia para uso global en el backend
respuesta_service = RespuestaEmpaticaService()