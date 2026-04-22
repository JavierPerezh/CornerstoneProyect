import json
import numpy as np
import os
from app.core.math_models import RegresionLogistica
from app.core.preprocessing import Preprocesador
from app.services.motor_reglas import MotorReglasClinicas  
from app.core.config import settings

class RiskService:
    """
    Orquestador de Decisiones Clinicas. 
    Combina Regresion Logistica (Matematica) + Motor de Reglas (Evidencia Medica).
    """

    def __init__(self):
        self.modelo = None
        self.preprocesador = Preprocesador()
        self.motor_reglas = MotorReglasClinicas()
        self.feature_order = []
        self._cargar_configuracion()

    def _cargar_configuracion(self):
        """Carga los pesos entrenados y parametros del escalador."""
        config_path = settings.model_path
        
        if not os.path.exists(config_path):
            # Fallback por si no se ha corrido el entrenamiento aun
            print(f"Advertencia: No se encontro {config_path}. Usando inicializacion por defecto.")
            return

        with open(config_path, "r") as f:
            config = json.load(f)

        self.preprocesador.load_params(config["scaler_params"])
        model_params = config["model_params"]
        
        self.modelo = RegresionLogistica(
            len(model_params["W"]), 
            len(model_params["W"][0])
        )
        self.modelo.load_parameters(model_params)
        self.feature_order = config["feature_order"]

    def procesar_evaluacion_completa(self, datos_madre_dict: dict):
        """
        Realiza la evaluacion dual: Estadistica y Normativa.
        """
        # 1. EVALUACION NORMATIVA (Motor de Reglas - Seguridad primero)
        alerta_reglas, recomendacion_reglas = self.motor_reglas.evaluar_estado(datos_madre_dict)

        # 2. EVALUACION ESTADISTICA (Regresion Logistica)
        try:
            vector_entrada = [datos_madre_dict[feat] for feat in self.feature_order]
            X_input = np.array([vector_entrada])
            X_scaled = self.preprocesador.transform_scaler(X_input)
            
            # Probabilidades por clase [bajo, medio, alto]
            probabilidades = self.modelo.forward(X_scaled)[0]
            pred_idx = np.argmax(probabilidades)
            alerta_ml = self.preprocesador.inv_label_map[pred_idx]
            confianza_ml = float(probabilidades[pred_idx])
        except Exception as e:
            print(f"Error en calculo ML: {e}")
            alerta_ml, confianza_ml = "error", 0.0

        # 3. LOGICA DE ARBITRAJE (Decision Final)
        # Si el motor de reglas detecta 'rojo', ignoramos el ML si este dice algo menor.
        
        jerarquia = {"verde": 0, "amarillo": 1, "rojo": 2}
        
        if jerarquia[alerta_reglas] >= jerarquia.get(alerta_ml, 0):
            nivel_final = alerta_reglas
            metodo = "Reglas Clinicas (Prioridad Seguridad)"
        else:
            nivel_final = alerta_ml
            metodo = "Modelo IA (Tendencia Estadistica)"

        return {
            "nivel_riesgo": nivel_final,
            "recomendacion_base": recomendacion_reglas,
            "detalle_tecnico": {
                "metodo_decisivo": metodo,
                "score_ml": confianza_ml,
                "alerta_ml": alerta_ml,
                "alerta_reglas": alerta_reglas
            }
        }

# Instancia unica para la API
risk_service = RiskService()
