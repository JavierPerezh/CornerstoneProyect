import unittest
import numpy as np
from app.core.preprocessing import Preprocesador

class TestPreprocessing(unittest.TestCase):
    def test_scaler_normalization(self):
        """Verifica que tras normalizar, la media sea cercana a 0."""
        data = np.array([[10, 20], [30, 40], [50, 60]])
        pre = Preprocesador()
        pre.fit_scaler(data)
        transformed = pre.transform_scaler(data)
        
        media_resultante = np.mean(transformed, axis=0)
        np.testing.assert_allclose(media_resultante, [0, 0], atol=1e-7)

    def test_one_hot_encoding(self):
        """Verifica la conversion de etiquetas a vectores binarios."""
        labels = ["bajo", "alto", "medio"]
        pre = Preprocesador()
        encoded = pre.encode_labels(labels)
        
        self.assertEqual(encoded.shape, (3, 3))
        self.assertEqual(np.sum(encoded), 3)