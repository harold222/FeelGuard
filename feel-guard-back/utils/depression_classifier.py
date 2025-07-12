import pickle
import re
import string
from typing import Dict, Optional
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

# Descargar recursos de NLTK si no están disponibles
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class DepressionClassifier:
    def __init__(self, model_path: str = "utils/depression_classifier_model.pkl"):
        """
        Inicializa el clasificador de depresión
        """
        self.model = None
        self.model_path = model_path
        self.load_model()
    
    def load_model(self):
        """
        Carga el modelo entrenado
        """
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"Modelo de depresión cargado desde: {self.model_path}")
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {self.model_path}")
            print("Asegúrate de que el modelo esté en la ubicación correcta")
            self.model = None
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
            self.model = None
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocesa el texto: convierte a minúsculas, elimina puntuación y stopwords
        """
        if pd.isna(text):
            return ""
        
        # Convertir a string si no lo es
        text = str(text)
        
        # Convertir a minúsculas
        text = text.lower()
        
        # Eliminar puntuación
        text = re.sub(f'[{string.punctuation}]', ' ', text)
        
        # Eliminar números
        text = re.sub(r'\d+', '', text)
        
        # Eliminar espacios extra
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Tokenización y eliminación de stopwords
        try:
            stop_words = set(stopwords.words('spanish'))
            tokens = word_tokenize(text)
            tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
            text = ' '.join(tokens)
        except:
            # Si hay problemas con NLTK, usar método simple
            pass
            
        return text
    
    def classify_text(self, text: str) -> Dict:
        """
        Clasifica un texto como depresivo o neutro
        """
        if self.model is None:
            return {
                'is_depression': False,
                'confidence': 0.0,
                'probability': [1.0, 0.0],
                'error': 'Modelo no disponible'
            }
        
        try:
            # Preprocesar el texto
            processed_text = self.preprocess_text(text)
            
            # Hacer predicción
            prediction = self.model.predict([processed_text])[0]
            probability = self.model.predict_proba([processed_text])[0]
            
            return {
                'is_depression': bool(prediction),
                'confidence': max(probability),
                'probability': probability.tolist(),
                'processed_text': processed_text
            }
        except Exception as e:
            return {
                'is_depression': False,
                'confidence': 0.0,
                'probability': [1.0, 0.0],
                'error': f'Error en clasificación: {str(e)}'
            }
    
    def is_depression_detected(self, text: str) -> bool:
        """
        Método simple para verificar si se detecta depresión
        """
        result = self.classify_text(text)
        return result.get('is_depression', False)

# Instancia global del clasificador
depression_classifier = DepressionClassifier() 