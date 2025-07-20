import React, { useState, useEffect } from 'react';
import type { UserAssessmentSummary } from '../types/ai';
import { aiService } from '../services/ai.service';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<UserAssessmentSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState(30);

  useEffect(() => {
    loadSummary();
  }, [period]);

  const loadSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await aiService.getUserAssessmentSummary(period);
      setSummary(data);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError('Error al cargar el resumen');
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'bajo': return '#4CAF50';
      case 'moderado': return '#FF9800';
      case 'alto': return '#F44336';
      case 'crítico': return '#9C27B0';
      // Mantener compatibilidad con inglés por si acaso
      case 'low': return '#4CAF50';
      case 'moderate': return '#FF9800';
      case 'high': return '#F44336';
      case 'critical': return '#9C27B0';
      default: return '#9E9E9E';
    }
  };

  const getAssessmentTypeColor = (type: string) => {
    switch (type) {
      case 'depression': return '#2196F3';
      case 'neutral': return '#4CAF50';
      default: return '#9E9E9E';
    }
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Cargando resumen...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="error-message">{error}</div>
        <button onClick={loadSummary} className="retry-btn">Reintentar</button>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="dashboard-container">
        <div className="no-data">No hay datos disponibles</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Dashboard de Salud Mental</h1>
        <div className="period-selector">
          <label>Período:</label>
          <select value={period} onChange={(e) => setPeriod(Number(e.target.value))}>
            <option value={7}>Últimos 7 días</option>
            <option value={30}>Últimos 30 días</option>
            <option value={90}>Últimos 90 días</option>
          </select>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Resumen general */}
        <div className="dashboard-card summary-card">
          <h3>Resumen General</h3>
          <div className="summary-stats">
            <div className="stat-item">
              <span className="stat-number">{summary.total_conversations}</span>
              <span className="stat-label">Conversaciones</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{summary.total_assessments}</span>
              <span className="stat-label">Evaluaciones</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{summary.period_days}</span>
              <span className="stat-label">Días</span>
            </div>
          </div>
        </div>

        {/* Niveles de riesgo */}
        <div className="dashboard-card">
          <h3>Niveles de Riesgo</h3>
          <div className="risk-chart">
            {Object.entries(summary.risk_levels_summary).map(([level, count]) => (
              <div key={level} className="risk-bar">
                <div className="risk-label">
                  <span 
                    className="risk-dot" 
                    style={{ backgroundColor: getRiskLevelColor(level) }}
                  ></span>
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </div>
                <div className="risk-progress">
                  <div 
                    className="risk-fill"
                    style={{ 
                      width: `${(count / summary.total_assessments) * 100}%`,
                      backgroundColor: getRiskLevelColor(level)
                    }}
                  ></div>
                  <span className="risk-count">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tipos de evaluación */}
        <div className="dashboard-card">
          <h3>Tipos de Evaluación</h3>
          <div className="assessment-chart">
            {Object.entries(summary.assessment_types_summary).map(([type, count]) => (
              <div key={type} className="assessment-item">
                <div className="assessment-label">
                  <span 
                    className="assessment-dot" 
                    style={{ backgroundColor: getAssessmentTypeColor(type) }}
                  ></span>
                  {type === 'depression' ? 'Depresión' : type === 'neutral' ? 'Neutral' : type.charAt(0).toUpperCase() + type.slice(1)}
                </div>
                <div className="assessment-count">{count}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Puntuación promedio */}
        <div className="dashboard-card">
          <h3>Puntuación Promedio de Riesgo</h3>
          <div className="average-score">
            <div 
              className="score-circle"
              style={{ 
                background: `conic-gradient(${getRiskLevelColor('high')} ${summary.average_risk_score * 100}%, #e0e0e0 0%)`
              }}
            >
              <span className="score-value">{summary.average_risk_score.toFixed(1)}</span>
            </div>
          </div>
        </div>

        {/* Recomendaciones */}
        <div className="dashboard-card recommendations-card">
          <h3>Recomendaciones</h3>
          <div className="recommendations-list">
            {summary.recommendations.map((rec, index) => (
              <div key={index} className="recommendation-item">
                <span className="recommendation-bullet">•</span>
                <span className="recommendation-text">{rec}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 