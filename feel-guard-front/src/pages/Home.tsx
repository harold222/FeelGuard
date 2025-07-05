import React from 'react';
import Formulario from '../components/Formulario';
import './Home.css';

const Home: React.FC = () => {
  return (
    <div className="home">
      <div className="home-content">
        <div className="home-header">
          <h1>Bienvenido a Feel Guard IA</h1>
        </div>
        <Formulario />
      </div>
    </div>
  );
};

export default Home; 