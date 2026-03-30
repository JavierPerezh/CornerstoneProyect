import pandas as pd
import numpy as np
import json
import os
from app.core.math_models import RegresionLogistica
from app.core.preprocessing import Preprocesador

def ejecutar_entrenamiento():
    """
    Orquesta el ciclo de vida del entrenamiento manual: carga, 
    preprocesamiento, optimizacion y persistencia.
    """
    print("--- Inicio de Entrenamiento ---")

    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    
    # Construir la ruta al CSV (asumiendo que esta en la misma carpeta training/)
    ruta_csv = os.path.join(directorio_actual, "datos_madres.csv")

    try:
        df = pd.read_csv(ruta_csv)
        print(f"Dataset cargado exitosamente desde: {ruta_csv}")
    except FileNotFoundError:
        print(f"Error critico: No se encontro el archivo en {ruta_csv}")
        return

    # 2. Preparacion de Matrices de NumPy
    X_raw = df.drop("riesgo", axis=1).values
    y_raw = df["riesgo"].values

    # 3. Preprocesamiento
    preprocesador = Preprocesador()
    preprocesador.fit_scaler(X_raw)
    
    X_scaled = preprocesador.transform_scaler(X_raw)
    y_one_hot = preprocesador.encode_labels(y_raw)

    # 4. Inicializacion del Modelo
    # 17 variables de entrada, 3 clases de salida (bajo, medio, alto)
    modelo = RegresionLogistica(n_features=17, n_classes=3, learning_rate=0.05)

    # 5. Bucle de Optimizacion (Descenso del Gradiente)
    epochs = 1500
    print(f"Entrenando durante {epochs} epocas...")
    
    for epoch in range(epochs):
        loss = modelo.entrenar_paso(X_scaled, y_one_hot)
        
        # Monitoreo de la convergencia cada 100 epocas
        if epoch % 100 == 0:
            print(f"Epoca {epoch}: Loss = {loss:.6f}")

    # 6. Evaluacion rapida (In-sample)
    predicciones_idx = modelo.predict(X_scaled)
    y_true_idx = np.argmax(y_one_hot, axis=1)
    accuracy = np.mean(predicciones_idx == y_true_idx)
    print(f"\nEntrenamiento completado. Precision final (Train Set): {accuracy * 100:.2f}%")

    # 7. Persistencia de Parametros (JSON)
    # Guardamos los pesos y los parametros del escalador para el Backend


    config_final = {
        "model_params": modelo.save_parameters(),
        "scaler_params": preprocesador.save_params(),
        "feature_order": list(df.drop("riesgo", axis=1).columns)
    }

    raiz_proyecto = os.path.dirname(os.path.dirname(directorio_actual))
    ruta_models = os.path.join(raiz_proyecto, "app", "models", "weights")
    
    os.makedirs(ruta_models, exist_ok=True)
    
    ruta_final_json = os.path.join(ruta_models, "parametros_finales.json")
    
    with open(ruta_final_json, "w") as f:
        json.dump(config_final, f, indent=4)
    
    print(f"Parametros exportados exitosamente a: {ruta_final_json}")

if __name__ == "__main__":
    ejecutar_entrenamiento()