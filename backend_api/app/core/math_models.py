import numpy as np

class RegresionLogistica:
    """
    Implementacion de Regresion Logistica Multinomial 
    utilizando descenso del gradiente para la optimizacion de parametros.
    """

    def __init__(self, n_features, n_classes, learning_rate=0.01):
        self.lr = learning_rate
        self.W = np.zeros((n_features, n_classes))
        self.b = np.zeros((1, n_classes))
        self.losses = []

    def _softmax(self, z):
        """
        Calcula la funcion Softmax.
        z: Matriz de puntajes logit (n_samples, n_classes)
        """
        exp_z = np.exp(z - np.max(z, axis=1, keepdims=True))
        return exp_z / np.sum(exp_z, axis=1, keepdims=True)

    def forward(self, X):
        """
        Calcula el paso hacia adelante (forward pass).
        z = XW + b
        """
        z = np.dot(X, self.W) + self.b
        return self._softmax(z)

    def calcular_costo(self, y_true_enc, y_pred):
        """
        Funcion de perdida: Entropia Cruzada Categorica (Cross-Entropy).
        """
        n_samples = y_true_enc.shape[0]
        loss = -1/n_samples * np.sum(y_true_enc * np.log(y_pred + 1e-15))
        return loss

    def entrenar_paso(self, X, y_true_enc):
        """
        Ejecuta una iteracion del descenso del gradiente.
        """
        n_samples = X.shape[0]
        
        # 1. Prediccion actual
        y_pred = self.forward(X)
        
        # 2. Calculo de gradientes
        # La derivada de Cross-Entropy respecto a Softmax es (y_pred - y_true)
        error = y_pred - y_true_enc
        dw = (1 / n_samples) * np.dot(X.T, error)
        db = (1 / n_samples) * np.sum(error, axis=0, keepdims=True)
        
        # 3. Actualizacion de parametros (Descenso del gradiente)
        self.W -= self.lr * dw
        self.b -= self.lr * db
        
        return self.calcular_costo(y_true_enc, y_pred)

    def predict(self, X):
        """
        Retorna el indice de la clase con mayor probabilidad.
        """
        probs = self.forward(X)
        return np.argmax(probs, axis=1)

    def save_parameters(self):
        """
        Retorna un diccionario con los parametros actuales para persistencia.
        """
        return {
            "W": self.W.tolist(),
            "b": self.b.tolist(),
            "lr": self.lr
        }

    def load_parameters(self, params):
        """
        Carga pesos y sesgos externos al modelo.
        """
        self.W = np.array(params["W"])
        self.b = np.array(params["b"])