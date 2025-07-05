import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import logo from '../assets/logo.jpeg';
import './Navbar.css';

const Navbar: React.FC = () => {
  const isAuthenticated = Boolean(localStorage.getItem('auth_token'));
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <img src={logo} alt="Feel Guard Logo" className="navbar-logo" />
          <span className="navbar-title">Feel Guard</span>
        </Link>
        
        <div className="navbar-menu">
          {!isAuthenticated && (
            <Link to="/" className="nav-link">
              Inicio
            </Link>
          )}
          {isAuthenticated && (
            <>
              <Link to="/ai-chat" className="nav-link">
                Interactuar
              </Link>
              <button className="nav-link nav-logout" onClick={handleLogout} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', font: 'inherit', padding: 0 }}>
                Salir
              </button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 