import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import type { FormData, FormErrors } from '../types/form';
import { formService, simulateApiDelay, setLoaderCallback } from '../services/api';
import FullScreenLoader from './FullScreenLoader';
import './Formulario.css';

const EMAIL_DEBOUNCE = 400;

const Formulario: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    nombre: '',
    edad: '',
    sexo: ''
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [emailExists, setEmailExists] = useState(false);
  const [showLoader, setShowLoader] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    setLoaderCallback(setShowLoader);
    return () => setLoaderCallback(() => {});
  }, []);

  // Debounce para validar email automáticamente
  useEffect(() => {
    if (!formData.email.trim() || errors.email) {
      setEmailExists(false);
      return;
    }
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      try {
        const registro = await formService.getRegistroByEmail(formData.email);
        setFormData({
          email: registro.email,
          nombre: registro.nombre,
          edad: registro.edad.toString(),
          sexo: registro.sexo
        });
        setEmailExists(true);
        setSubmitMessage({ type: 'success', text: 'El correo ya está registrado. Los datos han sido autocompletados.' });
      } catch {
        setEmailExists(false);
      }
    }, EMAIL_DEBOUNCE);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData.email]);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Validar email
    if (!formData.email.trim()) {
      newErrors.email = 'El correo electrónico es requerido';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'El correo electrónico no es válido';
    }

    // Validar nombre
    if (!formData.nombre.trim()) {
      newErrors.nombre = 'El nombre es requerido';
    } else if (formData.nombre.trim().length < 2) {
      newErrors.nombre = 'El nombre debe tener al menos 2 caracteres';
    }

    // Validar edad
    if (!formData.edad.trim()) {
      newErrors.edad = 'La edad es requerida';
    } else {
      const edadNum = parseInt(formData.edad);
      if (isNaN(edadNum) || edadNum < 1 || edadNum > 120) {
        newErrors.edad = 'La edad debe ser un número válido entre 1 y 120';
      }
    }

    // Validar sexo
    if (!formData.sexo.trim()) {
      newErrors.sexo = 'El sexo es requerido';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Limpiar error del campo cuando el usuario empiece a escribir
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }

    // Limpiar mensaje de envío
    if (submitMessage) {
      setSubmitMessage(null);
    }
    // Si el usuario cambia el email, desbloquear los campos y limpiar otros campos
    if (name === 'email') {
      setEmailExists(false);
      setFormData(prev => ({ ...prev, nombre: '', edad: '', sexo: '' }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) {
      console.log('Errores de validación:', errors);
      return;
    }
    setIsSubmitting(true);
    setSubmitMessage(null);
    try {
      const response = await formService.submitForm(formData);
      if (response.success) {
        setSubmitMessage({ type: 'success', text: response.message || 'Formulario enviado exitosamente!' });
        setEmailExists(false);
        if (response.token) {
          localStorage.setItem('auth_token', response.token);
          navigate('/ai-chat');
        }
      } else {
        setSubmitMessage({ type: 'error', text: response.error || 'Error al enviar el formulario' });
      }
    } catch {
      setSubmitMessage({ type: 'error', text: 'Error de conexión. Por favor, inténtalo de nuevo.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="formulario-container">
      {showLoader && <FullScreenLoader />}
      <h2>Ingresar</h2>
      {submitMessage && (
        <div className={`submit-message ${submitMessage.type}`}>{submitMessage.text}</div>
      )}
      <form onSubmit={handleSubmit} className="formulario">
        <div className="form-group">
          <label htmlFor="email">Correo Electrónico *</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            className={errors.email ? 'error' : ''}
            placeholder="ejemplo@correo.com"
            disabled={isSubmitting}
          />
          {errors.email && <span className="error-message">{errors.email}</span>}
        </div>
        <div className="form-group">
          <label htmlFor="nombre">Nombre *</label>
          <input
            type="text"
            id="nombre"
            name="nombre"
            value={formData.nombre}
            onChange={handleInputChange}
            className={errors.nombre ? 'error' : ''}
            placeholder="Ingrese su nombre completo"
            disabled={isSubmitting || emailExists}
          />
          {errors.nombre && <span className="error-message">{errors.nombre}</span>}
        </div>
        <div className="form-group">
          <label htmlFor="edad">Edad *</label>
          <input
            type="number"
            id="edad"
            name="edad"
            value={formData.edad}
            onChange={handleInputChange}
            className={errors.edad ? 'error' : ''}
            placeholder="Ingrese su edad"
            min="1"
            max="120"
            disabled={isSubmitting || emailExists}
          />
          {errors.edad && <span className="error-message">{errors.edad}</span>}
        </div>
        <div className="form-group">
          <label htmlFor="sexo">Sexo *</label>
          <select
            id="sexo"
            name="sexo"
            value={formData.sexo}
            onChange={handleInputChange}
            className={errors.sexo ? 'error' : ''}
            disabled={isSubmitting || emailExists}
          >
            <option value="">Seleccione</option>
            <option value="masculino">Masculino</option>
            <option value="femenino">Femenino</option>
            <option value="otro">Otro</option>
          </select>
          {errors.sexo && <span className="error-message">{errors.sexo}</span>}
        </div>
        <button type="submit" className="submit-btn" disabled={isSubmitting}>
          {isSubmitting ? 'Ingresando...' : 'Ingresar'}
        </button>
      </form>
    </div>
  );
};

export default Formulario; 