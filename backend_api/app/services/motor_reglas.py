from typing import Dict, Tuple

class MotorReglasClinicas:
    """
    Sistema experto que valida las 17 variables extraídas por el LLM.
    Basado en protocolos de la OMS (Postpartum Care) y ACOG.
    """

    def __init__(self):
        # Umbrales clínicos estándar
        self.UMBRAL_FIEBRE = 38.0
        self.UMBRAL_DOLOR_CRITICO = 8
        self.UMBRAL_PRESION_SISTOLICA = 140
        self.UMBRAL_PRESION_DIASTOLICA = 90

    def evaluar_estado(self, datos: Dict) -> Tuple[str, str]:
        """
        Evalúa las 20 reglas de seguridad.
        Retorna: (nivel_alerta: 'verde'|'amarillo'|'rojo', recomendacion: str)
        """
        
        # --- SECCIÓN 1: ALERTAS ROJAS (EMERGENCIA INMEDIATA) ---
        # 1. Hemorragia Postparto (OMS)
        if datos.get("sangrado_abundante") == 1:
            return "rojo", "Busca ayuda médica inmediata. El sangrado abundante puede ser una emergencia."
        
        # 2. Preeclampsia Tardía: Cefalea intensa (ACOG)
        if datos.get("dolor_cabecera", 0) >= 8 and datos.get("hinchazon_edema") == 1:
            return "rojo", "Alerta de preeclampsia: Dolor de cabeza intenso con hinchazón. Ve a urgencias."
        
        # 3. Sepsis Puerperal: Fiebre alta (SEGO)
        if datos.get("fiebre_madre", 0) >= self.UMBRAL_FIEBRE:
            return "rojo", "Fiebre alta detectada. Podría ser una infección; contacta a tu médico ahora."
        
        # 4. Salud del Recién Nacido: Fiebre en bebé
        if datos.get("fiebre_bebe", 0) == 1:
            return "rojo", "La fiebre en un recién nacido requiere evaluación pediátrica urgente."
        
        # 5. Ideación Suicida o Psicosis Postparto (DSM-V / OMS)
        if datos.get("estado_animo", 0) == 0 and datos.get("nivel_ansiedad", 0) >= 9:
            return "rojo", "Tu bienestar emocional es prioridad. Por favor, contacta a una línea de apoyo o profesional hoy mismo."

        # 6. Disnea (Dificultad respiratoria) - Riesgo de embolia
        if datos.get("dificultad_respiratoria") == 1:
            return "rojo", "Dificultad para respirar detectada. Acude a un centro de salud inmediatamente."

        # 7. Dolor torácico
        if datos.get("dolor_pecho") == 1:
            return "rojo", "El dolor en el pecho requiere evaluación médica urgente para descartar riesgos cardiovasculares."

        # --- SECCIÓN 2: ALERTAS AMARILLAS (SEGUIMIENTO EN 24H) ---
        # 8. Depresión Postparto Moderada (Escala Edimburgo adaptada)
        if datos.get("estado_animo") <= 2 and datos.get("apoyo_social") == 0:
            return "amarillo", "Parece que estás pasando un momento difícil. Sería bueno hablar con tu obstetra sobre cómo te sientes."
        
        # 9. Mastitis: Dolor en pecho + malestar
        if datos.get("dificultad_lactancia") == 1 and datos.get("nivel_dolor") >= 6:
            return "amarillo", "El dolor persistente en el pecho puede ser inicio de mastitis. Consulta con tu asesora de lactancia."

        # 10. Infección de herida (Cesárea/Episiotomía)
        if datos.get("dolor_herida") >= 6 or datos.get("secrecion_herida") == 1:
            return "amarillo", "Revisa tu herida quirúrgica. Si hay enrojecimiento o secreción, consulta a tu médico."

        # 11. Estreñimiento severo posparto
        if datos.get("dias_sin_evacuar", 0) >= 4:
            return "amarillo", "Aumenta la hidratación y fibra. Si el malestar persiste, contacta a tu médico."

        # 12. Retención urinaria o disuria
        if datos.get("dolor_al_orinar") == 1:
            return "amarillo", "El dolor al orinar puede indicar una infección urinaria, común en el posparto."

        # 13. Edema moderado en piernas
        if datos.get("hinchazon_piernas") == 1 and datos.get("dolor_cabecera") < 5:
            return "amarillo", "Mantén las piernas elevadas y reduce la sal. Si notas visión borrosa, avísame."

        # 14. Trastornos del sueño extremos
        if datos.get("horas_sueno", 8) <= 3:
            return "amarillo", "El agotamiento extremo afecta tu salud. Intenta delegar tareas para descansar al menos 4 horas seguidas."

        # --- SECCIÓN 3: ALERTAS VERDES (ACOMPAÑAMIENTO Y PREVENCIÓN) ---
        # 15. Lactancia establecida con dudas
        if datos.get("dificultad_lactancia") == 1 and datos.get("nivel_dolor") < 4:
            return "verde", "La lactancia es un proceso de aprendizaje. Estás haciendo un gran trabajo, ten paciencia."

        # 16. "Baby Blues" (Normalidad en los primeros 10 días)
        if datos.get("dias_posparto", 0) <= 10 and datos.get("estado_animo") == 2:
            return "verde", "Es normal sentir sensibilidad estos días. Se llama Baby Blues y suele pasar pronto."

        # 17. Vínculo con el bebé
        if datos.get("vinculo_bebe") >= 4:
            return "verde", "Me alegra saber que te sientes conectada con tu bebé. Ese vínculo es maravilloso."

        # 18. Actividad física leve
        if datos.get("actividad_fisica") == 0 and datos.get("dias_posparto") > 15:
            return "verde", "Cuando te sientas lista, caminar 10 minutos puede ayudarte a mejorar tu ánimo."

        # 19. Nutrición y apetito
        if datos.get("perdida_apetito") == 1:
            return "verde", "Recuerda alimentarte bien para recuperar energías. Pequeñas comidas frecuentes pueden ayudar."

        # 20. Regla por defecto (Normalidad)
        return "verde", "Todo parece estar dentro de lo esperado. Sigue descansando y disfrutando de tu bebé."

# Instancia global
motor_reglas = MotorReglasClinicas()