# Integración del Clasificador de Depresión en Feel Guard

## Resumen

Se ha integrado exitosamente un modelo de machine learning entrenado para clasificar textos en español como depresivos o neutros en el backend de Feel Guard. El modelo reemplaza el sistema anterior basado en diccionarios de palabras clave.

## Cambios Implementados

### 1. Nuevo Módulo de Clasificación
- **Archivo**: `utils/depression_classifier.py`
- **Función**: Carga y utiliza el modelo entrenado para clasificar textos
- **Características**:
  - Preprocesamiento de texto (limpieza, tokenización, eliminación de stopwords)
  - Clasificación binaria: depresión vs neutro
  - Retorna probabilidades y nivel de confianza

### 2. Actualización del Sistema de Evaluación
- **Archivo**: `utils/mental_health_assessment.py`
- **Cambios**:
  - Eliminación de diccionarios de palabras clave para estrés y ansiedad
  - Integración del modelo de clasificación de depresión
  - Simplificación a solo dos tipos: DEPRESSION y NEUTRAL
  - Mantenimiento de detección de crisis para emergencias

### 3. Actualización del Agente de IA
- **Archivo**: `utils/ai_agent.py`
- **Cambios**:
  - Uso del modelo de clasificación en lugar de detección por palabras clave
  - Simplificación de la lógica de determinación de tipo de evaluación
  - Mantenimiento de la detección de crisis para casos de emergencia

### 4. Actualización de Prompts
- **Archivo**: `utils/mental_health_prompts.py`
- **Cambios**:
  - Eliminación de prompts para estrés y ansiedad
  - Enfoque exclusivo en depresión y bienestar general
  - Mantenimiento de prompts para crisis y seguimiento

### 5. Actualización de Endpoints
- **Archivo**: `routes/ai.py`
- **Cambios**:
  - Inclusión de información de clasificación del modelo en las respuestas
  - Nuevo campo `depression_classification` en las respuestas de la API

## Estructura de Respuesta Actualizada

```json
{
  "output": "Respuesta de la IA...",
  "session_id": "uuid-session",
  "assessment": {
    "session_id": "uuid-session",
    "type": "depression",
    "risk_level": "high",
    "timestamp": "2024-01-01T12:00:00",
    "text_sample": "Me siento muy triste...",
    "depression_assessment": {
      "level": "Alto",
      "score": 0.85,
      "is_depression": true,
      "probability_neutral": 0.15,
      "probability_depression": 0.85,
      "timestamp": "2024-01-01T12:00:00"
    }
  },
  "risk_level": "high",
  "depression_classification": {
    "is_depression": true,
    "confidence": 0.85,
    "probability": [0.15, 0.85],
    "processed_text": "siento triste ganas vivir"
  }
}
```

## Instalación y Configuración

### 1. Dependencias
Agregar las siguientes dependencias al `requirements.txt`:
```
pandas>=1.3.0
numpy>=1.21.0
scikit-learn>=1.0.0
nltk>=3.6.0
```

### 2. Modelo Entrenado
- El archivo `depression_classifier_model.pkl` debe estar en `utils/`
- El modelo se carga automáticamente al iniciar la aplicación

### 3. Instalación
```bash
cd feel-guard-back
pip install -r requirements.txt
```

## Pruebas

### Script de Prueba
Ejecutar el script de prueba para verificar la integración:
```bash
python test_depression_classifier.py
```

### Ejemplos de Uso

#### Textos Depresivos (Clasificados como depresión):
- "Me siento muy triste y no tengo ganas de vivir"
- "No puedo más con esta vida, quiero desaparecer"
- "Me siento vacío por dentro, nada tiene sentido"

#### Textos Neutros (Clasificados como neutro):
- "Hoy es un día hermoso y estoy muy feliz"
- "Voy a salir con mis amigos a divertirme"
- "Estoy muy emocionado por el viaje de mañana"

## Ventajas de la Nueva Implementación

### 1. Mayor Precisión
- El modelo entrenado con 1,571 ejemplos tiene mayor precisión que la detección por palabras clave
- Precisión del modelo SVM: ~91%

### 2. Mejor Generalización
- El modelo puede detectar patrones complejos que no se capturan con palabras clave simples
- Maneja mejor variaciones en el lenguaje y expresiones

### 3. Probabilidades y Confianza
- Proporciona niveles de confianza para cada clasificación
- Permite tomar decisiones más informadas sobre el nivel de riesgo

### 4. Mantenimiento Simplificado
- Un solo modelo en lugar de múltiples diccionarios
- Más fácil de actualizar y mejorar

## Consideraciones de Seguridad

### 1. Detección de Crisis
- Se mantiene la detección de crisis para casos de emergencia
- Palabras clave críticas siguen siendo monitoreadas

### 2. Recursos de Emergencia
- Se incluyen recursos de emergencia en las respuestas cuando se detecta crisis
- Números de teléfono y líneas de ayuda

## Monitoreo y Logs

### 1. Logs de Clasificación
- Se registran las clasificaciones para análisis posterior
- Información de confianza y probabilidades

### 2. Métricas de Rendimiento
- Precisión del modelo en producción
- Tiempo de respuesta de clasificación

## Futuras Mejoras

### 1. Reentrenamiento del Modelo
- Recopilar más datos de usuarios reales
- Reentrenar el modelo con datos más específicos del dominio

### 2. Múltiples Modelos
- Considerar modelos específicos para diferentes tipos de depresión
- Modelos para otros problemas de salud mental

### 3. Análisis de Tendencias
- Implementar análisis de tendencias a largo plazo
- Detección de patrones temporales

## Troubleshooting

### Error: "Modelo no disponible"
- Verificar que el archivo `depression_classifier_model.pkl` esté en `utils/`
- Verificar permisos de lectura del archivo

### Error: "NLTK data not found"
- El script descarga automáticamente los recursos necesarios
- Si hay problemas de conexión, descargar manualmente:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

### Bajo Rendimiento
- Verificar que las dependencias estén instaladas correctamente
- Verificar que el modelo se haya cargado correctamente
- Revisar logs para errores específicos 