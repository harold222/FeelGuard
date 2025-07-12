import joblib
import numpy as np
from PIL import Image
import os
import io

class DepressionImageClassifier:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "depression_image_classifier_model.pkl")
        self.model = joblib.load(model_path)
        self.label_decoder = {0: "neutral", 1: "depression"}

    def preprocess_image(self, image_bytes, target_size=(64, 64)):
        img = Image.open(image_bytes)
        img = img.convert("L")  # Escala de grises
        img = img.resize(target_size)
        img = np.array(img) / 255.0
        return img.flatten().reshape(1, -1)

    def classify(self, image_bytes):
        features = self.preprocess_image(image_bytes)
        pred = self.model.predict(features)[0]
        proba = self.model.predict_proba(features)[0]
        return {
            "is_depression": bool(pred),
            "confidence": float(np.max(proba)),
            "probabilities": {
                "neutral": float(proba[0]),
                "depression": float(proba[1])
            },
            "label": self.label_decoder[pred]
        }

# Instancia global
image_classifier = DepressionImageClassifier() 