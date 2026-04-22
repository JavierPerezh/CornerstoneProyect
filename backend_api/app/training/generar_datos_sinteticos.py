import pandas as pd
import numpy as np

np.random.seed(42)
n_registros = 2000

def generar_dataset():
    data = []
    
    for _ in range(n_registros):
        # 1. Variables Independientes 
        dias_posparto = np.random.randint(1, 43)
        horas_sueno = np.random.normal(6, 1.5) 
        horas_sueno = np.clip(horas_sueno, 0, 12)
        
        nivel_dolor = np.random.randint(0, 11)
        fiebre_madre = np.random.choice([0, 1], p=[0.95, 0.05])
        fiebre_bebe = np.random.choice([0, 1], p=[0.96, 0.04])
        sangrado_abundante = np.random.choice([0, 1], p=[0.98, 0.02])
        
        estado_animo = np.random.randint(1, 6)
        apoyo_social = np.random.choice([0, 1], p=[0.2, 0.8])
        dificultad_lactancia = np.random.choice([0, 1], p=[0.7, 0.3])
        llanto_bebe = np.random.randint(1, 6)
        dolor_cabecera = np.random.randint(0, 6) 
        hinchazon_edema = np.random.choice([0, 1], p=[0.9, 0.1])
        nivel_ansiedad = np.random.randint(1, 6)
        actividad_fisica = np.random.choice([0, 1], p=[0.3, 0.7])
        perdida_apetito = np.random.choice([0, 1], p=[0.9, 0.1])
        vinculo_bebe = np.random.randint(2, 6) 
        tipo_parto = np.random.choice([0, 1])

        score = (
            (7 - horas_sueno) * 0.8 + 
            (nivel_dolor * 0.4) + 
            (fiebre_madre * 4.0) + 
            (fiebre_bebe * 5.0) + 
            (sangrado_abundante * 8.0) + 
            (4 - estado_animo) * 1.2 + 
            (2 if apoyo_social == 0 else 0) +
            (dolor_cabecera * 0.5) +
            (hinchazon_edema * 1.5) +
            (nivel_ansiedad * 0.8)
        )

        if sangrado_abundante == 1 or fiebre_bebe == 1 or score > 18:
            riesgo = "alto"
        elif score > 8:
            riesgo = "medio"
        else:
            riesgo = "bajo"

        data.append([
            dias_posparto, round(horas_sueno, 1), nivel_dolor, fiebre_madre, fiebre_bebe,
            sangrado_abundante, estado_animo, apoyo_social, dificultad_lactancia,
            llanto_bebe, dolor_cabecera, hinchazon_edema, nivel_ansiedad,
            actividad_fisica, perdida_apetito, vinculo_bebe, tipo_parto, riesgo
        ])

    columnas = [
        "dias_posparto", "horas_sueno", "nivel_dolor", "fiebre_madre", "fiebre_bebe",
        "sangrado_abundante", "estado_animo", "apoyo_social", "dificultad_lactancia",
        "llanto_bebe", "dolor_cabecera", "hinchazon_edema", "nivel_ansiedad",
        "actividad_fisica", "perdida_apetito", "vinculo_bebe", "tipo_parto", "riesgo"
    ]
    
    df = pd.DataFrame(data, columns=columnas)
    df.to_csv("datos_madres.csv", index=False)
    print("Dataset re-generado con éxito.")
    print("\nDistribución de Riesgos:")
    print(df['riesgo'].value_counts(normalize=True) * 100)

if __name__ == "__main__":
    generar_dataset()