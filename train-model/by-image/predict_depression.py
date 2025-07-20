import joblib
import cv2
import numpy as np
from PIL import Image
import os
import argparse

class DepressionPredictor:
    def __init__(self, model_path='depression_classifier_model.pkl'):
        """
        Inicializa el predictor con el modelo entrenado
        """
        try:
            self.model = joblib.load(model_path)
            print(f"Modelo cargado exitosamente desde: {model_path}")
        except FileNotFoundError:
            print(f"Error: No se encontró el modelo en {model_path}")
            print("Asegúrate de entrenar el modelo primero.")
            return None
        
        self.label_decoder = {0: 'Neutral', 1: 'Depresión'}
    
    def preprocess_image(self, image_path, target_size=(64, 64)):
        """
        Preprocesa una imagen para la predicción
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
    
    def predict(self, image_path):
        """
        Hace una predicción para una imagen
        """
        if self.model is None:
            print("Error: Modelo no cargado")
            return None
        
        # Preprocesar imagen
        features = self.preprocess_image(image_path)
        
        if features is None:
            return None
        
        # Hacer predicción
        prediction = self.model.predict([features])[0]
        probabilities = self.model.predict_proba([features])[0]
        
        # Decodificar resultado
        predicted_label = self.label_decoder[prediction]
        confidence = probabilities[prediction]
        
        return {
            'prediction': predicted_label,
            'confidence': confidence,
            'probabilities': {
                'Neutral': probabilities[0],
                'Depresión': probabilities[1]
            }
        }
    
    def predict_batch(self, image_paths):
        """
        Hace predicciones para múltiples imágenes
        """
        results = []
        
        for image_path in image_paths:
            result = self.predict(image_path)
            if result is not None:
                result['image_path'] = image_path
                results.append(result)
            else:
                print(f"No se pudo procesar: {image_path}")
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Clasificador de Depresión en Imágenes')
    parser.add_argument('--image', type=str, help='Ruta de la imagen a clasificar')
    parser.add_argument('--folder', type=str, help='Carpeta con imágenes para clasificar')
    parser.add_argument('--model', type=str, default='depression_classifier_model.pkl', 
                       help='Ruta del modelo entrenado')
    
    args = parser.parse_args()
    
    # Inicializar predictor
    predictor = DepressionPredictor(args.model)
    
    if predictor.model is None:
        return
    
    # Clasificar una imagen específica
    if args.image:
        if not os.path.exists(args.image):
            print(f"Error: La imagen {args.image} no existe")
            return
        
        print(f"\nClasificando imagen: {args.image}")
        result = predictor.predict(args.image)
        
        if result:
            print(f"\nResultado:")
            print(f"Predicción: {result['prediction']}")
            print(f"Confianza: {result['confidence']:.4f}")
            print(f"Probabilidades:")
            print(f"  - Neutral: {result['probabilities']['Neutral']:.4f}")
            print(f"  - Depresión: {result['probabilities']['Depresión']:.4f}")
    
    # Clasificar múltiples imágenes de una carpeta
    elif args.folder:
        if not os.path.exists(args.folder):
            print(f"Error: La carpeta {args.folder} no existe")
            return
        
        # Obtener todas las imágenes de la carpeta
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        image_paths = []
        
        for file in os.listdir(args.folder):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_paths.append(os.path.join(args.folder, file))
        
        if not image_paths:
            print(f"No se encontraron imágenes en {args.folder}")
            return
        
        print(f"\nClasificando {len(image_paths)} imágenes de: {args.folder}")
        results = predictor.predict_batch(image_paths)
        
        print(f"\nResultados:")
        print("-" * 80)
        for result in results:
            print(f"Imagen: {os.path.basename(result['image_path'])}")
            print(f"Predicción: {result['prediction']} (Confianza: {result['confidence']:.4f})")
            print("-" * 40)
    
    else:
        print("Uso:")
        print("  python predict_depression.py --image ruta/imagen.jpg")
        print("  python predict_depression.py --folder ruta/carpeta")
        print("\nEjemplos:")
        print("  python predict_depression.py --image test_image.jpg")
        print("  python predict_depression.py --folder ./test_images/")

if __name__ == "__main__":
    main() 