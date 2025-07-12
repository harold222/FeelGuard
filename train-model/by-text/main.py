import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline
import pickle
import re
import string
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
    def __init__(self):
        self.pipeline = None
        self.vectorizer = None
        self.model = None
        
    def preprocess_text(self, text):
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
    
    def load_data(self, file_path):
        """
        Carga y preprocesa el dataset
        """
        print("Cargando dataset...")
        df = pd.read_csv(file_path)
        
        print(f"Dataset cargado: {len(df)} filas")
        print(f"Distribución de clases:")
        print(df['IS_DEPRESSION'].value_counts())
        
        # Preprocesar textos
        print("Preprocesando textos...")
        df['processed_text'] = df['TWEET_TEXT'].apply(self.preprocess_text)
        
        # Eliminar filas con texto vacío después del preprocesamiento
        df = df[df['processed_text'].str.len() > 0]
        
        print(f"Después del preprocesamiento: {len(df)} filas")
        
        return df
    
    def train_model(self, df, model_type='logistic'):
        """
        Entrena el modelo especificado
        """
        X = df['processed_text']
        y = df['IS_DEPRESSION']
        
        # Dividir en train y test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Conjunto de entrenamiento: {len(X_train)} muestras")
        print(f"Conjunto de prueba: {len(X_test)} muestras")
        
        # Crear pipeline
        if model_type == 'logistic':
            self.pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
                ('classifier', LogisticRegression(random_state=42, max_iter=1000))
            ])
        elif model_type == 'random_forest':
            self.pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
                ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
            ])
        elif model_type == 'svm':
            self.pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
                ('classifier', SVC(kernel='linear', random_state=42, probability=True))
            ])
        else:
            raise ValueError("model_type debe ser 'logistic', 'random_forest' o 'svm'")
        
        # Entrenar modelo
        print(f"Entrenando modelo {model_type}...")
        self.pipeline.fit(X_train, y_train)
        
        # Evaluar modelo
        y_pred = self.pipeline.predict(X_test)
        
        print("\n=== RESULTADOS DEL MODELO ===")
        print(f"Precisión: {accuracy_score(y_test, y_pred):.4f}")
        print("\nReporte de clasificación:")
        print(classification_report(y_test, y_pred, target_names=['Neutro', 'Depresión']))
        
        print("\nMatriz de confusión:")
        print(confusion_matrix(y_test, y_pred))
        
        return X_test, y_test, y_pred
    
    def predict_text(self, text):
        """
        Predice si un texto es depresivo o no
        """
        if self.pipeline is None:
            raise ValueError("El modelo no ha sido entrenado")
        
        processed_text = self.preprocess_text(text)
        prediction = self.pipeline.predict([processed_text])[0]
        probability = self.pipeline.predict_proba([processed_text])[0]
        
        return {
            'prediction': prediction,
            'probability': probability,
            'is_depression': bool(prediction),
            'confidence': max(probability)
        }
    
    def save_model(self, file_path):
        """
        Guarda el modelo entrenado
        """
        if self.pipeline is None:
            raise ValueError("No hay modelo para guardar")
        
        with open(file_path, 'wb') as f:
            pickle.dump(self.pipeline, f)
        print(f"Modelo guardado en: {file_path}")
    
    def load_model(self, file_path):
        """
        Carga un modelo guardado
        """
        with open(file_path, 'rb') as f:
            self.pipeline = pickle.load(f)
        print(f"Modelo cargado desde: {file_path}")

def main():
    # Crear instancia del clasificador
    classifier = DepressionClassifier()
    
    # Cargar datos
    df = classifier.load_data('dataset_depression_es.csv')
    
    # Entrenar diferentes modelos
    models = ['logistic', 'random_forest', 'svm']
    
    best_model = None
    best_accuracy = 0
    
    for model_type in models:
        print(f"\n{'='*50}")
        print(f"ENTRENANDO MODELO: {model_type.upper()}")
        print(f"{'='*50}")
        
        # Crear nueva instancia para cada modelo
        temp_classifier = DepressionClassifier()
        temp_classifier.load_data('dataset_depression_es.csv')
        
        X_test, y_test, y_pred = temp_classifier.train_model(df, model_type)
        accuracy = accuracy_score(y_test, y_pred)
        
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = temp_classifier
            best_model_type = model_type
    
    print(f"\n{'='*50}")
    print(f"MEJOR MODELO: {best_model_type.upper()} (Precisión: {best_accuracy:.4f})")
    print(f"{'='*50}")
    
    # Guardar el mejor modelo
    best_model.save_model('depression_classifier_model.pkl')
    
    # Ejemplos de uso
    print("\n=== EJEMPLOS DE PREDICCIÓN ===")
    test_texts = [
        "Me siento muy triste y no tengo ganas de vivir",
        "Hoy es un día hermoso y estoy muy feliz",
        "No puedo más con esta vida, quiero desaparecer",
        "Voy a salir con mis amigos a divertirme",
        "Me siento vacío por dentro, nada tiene sentido"
    ]
    
    for text in test_texts:
        result = best_model.predict_text(text)
        print(f"\nTexto: {text}")
        print(f"Predicción: {'Depresión' if result['is_depression'] else 'Neutro'}")
        print(f"Confianza: {result['confidence']:.4f}")
        print(f"Probabilidades: [Neutro: {result['probability'][0]:.4f}, Depresión: {result['probability'][1]:.4f}]")

if __name__ == "__main__":
    main()
