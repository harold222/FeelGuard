import React from 'react';
import { Link } from 'react-router-dom';
import Formulario from '../components/Formulario';
import './Home.css';

const Home: React.FC = () => {
  const isAuthenticated = Boolean(localStorage.getItem('auth_token'));

  return (
    <div className="home">
      <div className="home-content">
        <div className="home-header">
          <h1>Bienvenido a Feel Guard IA</h1>
          <p className="home-subtitle">
            Tu asistente de salud mental inteligente
          </p>
        </div>

        {!isAuthenticated ? (
          <div className="home-sections">
            <div className="features-section">
              <h2>Características Principales</h2>
              <div className="features-grid">
                <div className="feature-card">
                  <div className="feature-icon">🤖</div>
                  <h3>Chat Inteligente</h3>
                  <p>Conversa con nuestra IA especializada en salud mental</p>
                </div>
                <div className="feature-card">
                  <div className="feature-icon">📈</div>
                  <h3>Dashboard</h3>
                  <p>Seguimiento de tu progreso y recomendaciones personalizadas</p>
                </div>
                <div className="feature-card">
                  <div className="feature-icon">🚨</div>
                  <h3>Detección de Crisis</h3>
                  <p>Identificación automática de situaciones de riesgo</p>
                </div>
              </div>
            </div>

            <div className="login-section">
              <h2>Comienza tu viaje</h2>
              <p>Regístrate para acceder a todas las funcionalidades</p>
              <Formulario />
            </div>
          </div>
        ) : (
          <div className="authenticated-home">
            <div className="welcome-message">
              <h2>¡Bienvenido de vuelta!</h2>
              <p>¿En qué te puedo ayudar hoy?</p>
            </div>
            
            <div className="quick-actions">
              <Link to="/ai-chat" className="action-card">
                <div className="action-icon">💬</div>
                <h3>Iniciar Chat</h3>
                <p>Conversa con la IA sobre cómo te sientes</p>
              </Link>
              
              <Link to="/dashboard" className="action-card">
                <div className="action-icon">📊</div>
                <h3>Ver Dashboard</h3>
                <p>Revisa tu progreso y evaluaciones</p>
              </Link>
            </div>

            <div className="tips-section">
              <h3>💡 Consejos para hoy</h3>
              <ul>
                <li>Practica la respiración profunda durante 5 minutos</li>
                <li>Mantén un diario de gratitud</li>
                <li>Haz ejercicio ligero o sal a caminar</li>
                <li>Conecta con amigos o familiares</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home; 