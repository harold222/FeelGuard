import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
import joblib
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

class DepressionImageClassifier:
    def __init__(self):
        self.model = None
        self.feature_extractor = None
        self.label_encoder = {'Sad': 1, 'Neutral': 0}  # 1 = Depresión, 0 = Neutral
        
    def load_and_preprocess_image(self, image_path, target_size=(64, 64)):
        """
        Carga y preprocesa una imagen
        """
        try:
            # Intentar cargar con OpenCV
            img = cv2.imread(image_path)
            if img is None:
                # Si falla, intentar con PIL
                img = Image.open(image_path)
                img = np.array(img)
                if len(img.shape) == 3 and img.shape[2] == 4:  # RGBA
                    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
                elif len(img.shape) == 3 and img.shape[2] == 3:  # RGB
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            # Convertir a escala de grises
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Redimensionar
            img = cv2.resize(img, target_size)
            
            # Normalizar
            img = img / 255.0
            
            return img.flatten()  # Aplanar para el clasificador
            
        except Exception as e:
            print(f"Error procesando imagen {image_path}: {e}")
            return None
    
    def extract_features(self, image_paths, labels):
        """
        Extrae características de todas las imágenes
        """
        features = []
        valid_labels = []
        
        print("Extrayendo características de las imágenes...")
        for i, (path, label) in enumerate(tqdm(zip(image_paths, labels), total=len(image_paths))):
            # Construir ruta completa
            full_path = os.path.join(os.getcwd(), path)
            
            # Extraer características
            img_features = self.load_and_preprocess_image(full_path)
            
            if img_features is not None:
                features.append(img_features)
                valid_labels.append(self.label_encoder[label])
            else:
                print(f"Saltando imagen {path} - no se pudo procesar")
        
        return np.array(features), np.array(valid_labels)
    
    def train_model(self, X_train, y_train, model_type='random_forest'):
        """
        Entrena el modelo seleccionado
        """
        print(f"Entrenando modelo {model_type}...")
        
        if model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'svm':
            self.model = SVC(
                kernel='rbf',
                C=1.0,
                random_state=42,
                probability=True
            )
        elif model_type == 'mlp':
            self.model = MLPClassifier(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1
            )
        else:
            raise ValueError("model_type debe ser 'random_forest', 'svm', o 'mlp'")
        
        self.model.fit(X_train, y_train)
        print("Modelo entrenado exitosamente!")
    
    def evaluate_model(self, X_test, y_test):
        """
        Evalúa el modelo y muestra métricas
        """
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)
        
        # Métricas
        accuracy = accuracy_score(y_test, y_pred)
        
        print("\n" + "="*50)
        print("RESULTADOS DEL MODELO")
        print("="*50)
        print(f"Accuracy: {accuracy:.4f}")
        
        # Reporte de clasificación
        print("\nReporte de Clasificación:")
        print(classification_report(y_test, y_pred, 
                                 target_names=['Neutral', 'Depresión']))
        
        # Matriz de confusión
        cm = confusion_matrix(y_test, y_pred)
        print("\nMatriz de Confusión:")
        print(cm)
        
        # Visualizar matriz de confusión
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['Neutral', 'Depresión'],
                   yticklabels=['Neutral', 'Depresión'])
        plt.title('Matriz de Confusión')
        plt.ylabel('Etiqueta Real')
        plt.xlabel('Etiqueta Predicha')
        plt.tight_layout()
        plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return accuracy, y_pred, y_pred_proba
    
    def save_model(self, filename='depression_classifier_model.pkl'):
        """
        Guarda el modelo entrenado
        """
        if self.model is not None:
            joblib.dump(self.model, filename)
            print(f"Modelo guardado como: {filename}")
        else:
            print("No hay modelo para guardar!")

def main():
    print("="*60)
    print("ENTRENAMIENTO DEL MODELO DE CLASIFICACIÓN DE DEPRESIÓN")
    print("="*60)
    
    # Cargar datos procesados
    print("\n1. Cargando datos procesados...")
    try:
        df = pd.read_csv('data_processed.csv')
        print(f"Datos cargados: {len(df)} imágenes")
        print(f"Distribución de etiquetas:")
        print(df['label'].value_counts())
    except FileNotFoundError:
        print("Error: No se encontró el archivo data_processed.csv")
        print("Asegúrate de ejecutar primero el script de procesamiento de datos.")
        return
    
    # Preparar datos
    print("\n2. Preparando datos...")
    image_paths = df['path'].values
    labels = df['label'].values
    
    # Crear clasificador
    classifier = DepressionImageClassifier()
    
    # Extraer características
    print("\n3. Extrayendo características...")
    features, encoded_labels = classifier.extract_features(image_paths, labels)
    
    if len(features) == 0:
        print("Error: No se pudieron procesar imágenes. Verifica las rutas.")
        return
    
    print(f"Características extraídas: {features.shape}")
    print(f"Etiquetas procesadas: {len(encoded_labels)}")
    
    # Dividir datos
    print("\n4. Dividiendo datos en train/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        features, encoded_labels, 
        test_size=0.2, 
        random_state=42, 
        stratify=encoded_labels
    )
    
    print(f"Train: {X_train.shape[0]} muestras")
    print(f"Test: {X_test.shape[0]} muestras")
    
    # Entrenar modelo (puedes cambiar el tipo de modelo)
    print("\n5. Entrenando modelo...")
    model_type = 'random_forest'  # Opciones: 'random_forest', 'svm', 'mlp'
    classifier.train_model(X_train, y_train, model_type)
    
    # Evaluar modelo
    print("\n6. Evaluando modelo...")
    accuracy, predictions, probabilities = classifier.evaluate_model(X_test, y_test)
    
    # Guardar modelo
    print("\n7. Guardando modelo...")
    classifier.save_model()
    
    print("\n" + "="*60)
    print("ENTRENAMIENTO COMPLETADO")
    print("="*60)
    print(f"Modelo guardado como: depression_classifier_model.pkl")
    print(f"Accuracy final: {accuracy:.4f}")
    print("Matriz de confusión guardada como: confusion_matrix.png")

if __name__ == "__main__":
    main() 