import numpy as np

class Preprocesador:
    """
    Clase encargada de la transformacion de datos crudos a tensores 
    para el calculo matricial.
    """

    def __init__(self):
        self.mean = None
        self.std = None
        self.label_map = {"bajo": 0, "medio": 1, "alto": 2}
        self.inv_label_map = {0: "bajo", 1: "medio", 2: "alto"}

    def fit_scaler(self, X):
        """
        Calcula la media y desviacion estandar del conjunto de entrenamiento.
        X: Matriz de caracteristicas (n_samples, n_features)
        """
        self.mean = np.mean(X, axis=0)
        self.std = np.std(X, axis=0)
        # Evitar division por cero en variables constantes
        self.std[self.std == 0] = 1.0

    def transform_scaler(self, X):
        """
        Aplica la normalizacion Z-score: (x - mu) / sigma
        """
        if self.mean is None or self.std is None:
            raise ValueError("El escalador debe ser ajustado (fit) antes de transformar.")
        return (X - self.mean) / self.std

    def encode_labels(self, y_text):
        """
        Convierte etiquetas de texto a One-Hot Encoding.
        Retorna matriz de (n_samples, n_classes)
        """
        n_samples = len(y_text)
        n_classes = len(self.label_map)
        y_indices = np.array([self.label_map[label] for label in y_text])
        
        # Inicializacion de matriz identidad expandida
        one_hot = np.zeros((n_samples, n_classes))
        one_hot[np.arange(n_samples), y_indices] = 1
        return one_hot

    def decode_predictions(self, y_indices):
        """
        Convierte indices numericos de vuelta a etiquetas de texto.
        """
        return [self.inv_label_map[idx] for idx in y_indices]

    def save_params(self):
        """
        Exporta parametros para persistencia en formato JSON compatible.
        """
        return {
            "mean": self.mean.tolist(),
            "std": self.std.tolist()
        }

    def load_params(self, params):
        """
        Carga parametros de normalizacion previos.
        """
        self.mean = np.array(params["mean"])
        self.std = np.array(params["std"])