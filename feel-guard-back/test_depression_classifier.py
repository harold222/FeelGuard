#!/usr/bin/env python3
"""
Script de prueba para verificar la integración del clasificador de depresión
"""

import sys
import os

# Agregar el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.depression_classifier import depression_classifier
from utils.mental_health_assessment import mental_health_assessment, AssessmentType

def test_depression_classifier():
    """Prueba el clasificador de depresión con ejemplos"""
    
    print("=== PRUEBA DEL CLASIFICADOR DE DEPRESIÓN ===\n")
    
    # Ejemplos de texto
    test_cases = [
        {
            "text": "Me siento muy triste y no tengo ganas de vivir",
            "expected": "depression"
        },
        {
            "text": "Hoy es un día hermoso y estoy muy feliz",
            "expected": "neutral"
        },
        {
            "text": "No puedo más con esta vida, quiero desaparecer",
            "expected": "depression"
        },
        {
            "text": "Voy a salir con mis amigos a divertirme",
            "expected": "neutral"
        },
        {
            "text": "Me siento vacío por dentro, nada tiene sentido",
            "expected": "depression"
        },
        {
            "text": "Estoy muy emocionado por el viaje de mañana",
            "expected": "neutral"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        expected = test_case["expected"]
        
        print(f"Prueba {i}:")
        print(f"Texto: {text}")
        
        # Clasificar con el modelo
        classification = depression_classifier.classify_text(text)
        is_depression = classification.get('is_depression', False)
        confidence = classification.get('confidence', 0.0)
        probability = classification.get('probability', [0.0, 0.0])
        
        result = "depression" if is_depression else "neutral"
        
        print(f"Resultado: {result}")
        print(f"Confianza: {confidence:.4f}")
        print(f"Probabilidades: [Neutro: {probability[0]:.4f}, Depresión: {probability[1]:.4f}]")
        print(f"Esperado: {expected}")
        print(f"✓ Correcto" if result == expected else f"✗ Incorrecto")
        print("-" * 50)
    
    print("\n=== PRUEBA DE EVALUACIÓN DE SALUD MENTAL ===\n")
    
    # Probar la evaluación de salud mental
    for i, test_case in enumerate(test_cases[:3], 1):
        text = test_case["text"]
        
        print(f"Evaluación {i}:")
        print(f"Texto: {text}")
        
        # Determinar tipo de evaluación
        assessment_type = mental_health_assessment.determine_assessment_type(text)
        
        # Crear evaluación completa
        assessment = mental_health_assessment.create_assessment(
            session_id="test_session",
            text=text,
            assessment_type=assessment_type
        )
        
        print(f"Tipo de evaluación: {assessment.get('type', 'N/A')}")
        print(f"Nivel de riesgo: {assessment.get('risk_level', 'N/A')}")
        
        if assessment.get('depression_assessment'):
            dep_assessment = assessment['depression_assessment']
            print(f"Nivel de depresión: {dep_assessment.get('level', 'N/A')}")
            print(f"Puntuación: {dep_assessment.get('score', 'N/A')}")
        
        print("-" * 50)

def test_crisis_detection():
    """Prueba la detección de crisis"""
    
    print("\n=== PRUEBA DE DETECCIÓN DE CRISIS ===\n")
    
    crisis_texts = [
        "Me quiero suicidar",
        "No puedo más con esta vida",
        "Quiero acabar con todo",
        "Me siento muy triste hoy",
        "Hoy es un día normal"
    ]
    
    for i, text in enumerate(crisis_texts, 1):
        is_crisis = mental_health_assessment.detect_crisis(text)
        print(f"Texto {i}: {text}")
        print(f"¿Es crisis?: {is_crisis}")
        print("-" * 30)

if __name__ == "__main__":
    try:
        test_depression_classifier()
        test_crisis_detection()
        print("\n✅ Todas las pruebas completadas exitosamente!")
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc() 