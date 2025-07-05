import React from 'react';
import './FullScreenLoader.css';

const FullScreenLoader: React.FC = () => (
  <div className="fullscreen-loader-overlay">
    <div className="fullscreen-loader-spinner"></div>
    <div className="fullscreen-loader-text">Cargando...</div>
  </div>
);

export default FullScreenLoader; 