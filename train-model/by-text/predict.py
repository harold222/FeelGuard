import pickle
import sys

def load_model(model_path='depression_classifier_model.pkl'):
    """
    Carga el modelo entrenado
    """
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print(f"Modelo cargado desde: {model_path}")
        return model
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {model_path}")
        print("Primero debes entrenar el modelo ejecutando main.py")
        return None

def predict_text(model, text):
    """
    Predice si un texto es depresivo o no
    """
    try:
        prediction = model.predict([text])[0]
        probability = model.predict_proba([text])[0]
        
        return {
            'prediction': prediction,
            'probability': probability,
            'is_depression': bool(prediction),
            'confidence': max(probability)
        }
    except Exception as e:
        print(f"Error al hacer predicción: {e}")
        return None

def main():
    # Cargar modelo
    model = load_model()
    if model is None:
        return
    
    print("\n=== CLASIFICADOR DE DEPRESIÓN ===")
    print("Escribe 'salir' para terminar")
    print("Escribe 'ejemplos' para ver ejemplos")
    
    while True:
        print("\n" + "="*50)
        text = input("Ingresa un texto para clasificar: ").strip()
        
        if text.lower() == 'salir':
            print("¡Hasta luego!")
            break
        elif text.lower() == 'ejemplos':
            print("\n=== EJEMPLOS ===")
            examples = [
                "Me siento muy triste y no tengo ganas de vivir",
                "Hoy es un día hermoso y estoy muy feliz",
                "No puedo más con esta vida, quiero desaparecer",
                "Voy a salir con mis amigos a divertirme",
                "Me siento vacío por dentro, nada tiene sentido",
                "Estoy muy emocionado por el viaje de mañana",
                "La vida no tiene sentido, todo es inútil",
                "Me encanta pasar tiempo con mi familia"
            ]
            
            for i, example in enumerate(examples, 1):
                result = predict_text(model, example)
                if result:
                    status = "DEPRESIÓN" if result['is_depression'] else "NEUTRO"
                    print(f"{i}. {example}")
                    print(f"   Resultado: {status} (Confianza: {result['confidence']:.2f})")
            continue
        elif not text:
            print("Por favor ingresa un texto válido")
            continue
        
        # Hacer predicción
        result = predict_text(model, text)
        if result:
            print(f"\nTexto: {text}")
            print(f"Clasificación: {'DEPRESIÓN' if result['is_depression'] else 'NEUTRO'}")
            print(f"Confianza: {result['confidence']:.4f}")
            print(f"Probabilidades:")
            print(f"  - Neutro: {result['probability'][0]:.4f}")
            print(f"  - Depresión: {result['probability'][1]:.4f}")

if __name__ == "__main__":
    main() 