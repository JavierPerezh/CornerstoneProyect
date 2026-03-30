import unittest
import numpy as np
from app.core.math_models import RegresionLogistica

class TestMathModels(unittest.TestCase):
    def setUp(self):
        self.n_features = 17
        self.n_classes = 3
        self.model = RegresionLogistica(self.n_features, self.n_classes)

    def test_softmax_distribution(self):
        """Verifica que las probabilidades sumen 1 (Propiedad estocastica)."""
        z = np.array([[1.0, 2.0, 3.0], [5.0, 0.0, 1.0]])
        probs = self.model._softmax(z)
        sum_probs = np.sum(probs, axis=1)
        np.testing.assert_allclose(sum_probs, [1.0, 1.0])

    def test_forward_dimensions(self):
        """Verifica que el output tenga la forma (muestras, clases)."""
        X = np.random.randn(5, self.n_features)
        output = self.model.forward(X)
        self.assertEqual(output.shape, (5, self.n_classes))

    def test_gradient_update(self):
        """Verifica que el costo disminuya tras un paso de entrenamiento."""
        X = np.random.randn(10, self.n_features)
        y_true = np.zeros((10, self.n_classes))
        y_true[:, 0] = 1  # Todos son clase 0
        
        initial_loss = self.model.entrenar_paso(X, y_true)
        final_loss = self.model.entrenar_paso(X, y_true)
        self.assertLess(final_loss, initial_loss)