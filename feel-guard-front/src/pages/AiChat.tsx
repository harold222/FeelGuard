import React, { useState, useRef, useEffect } from 'react';
import type { ChatMessage, Assessment } from '../types/ai';
import { aiService } from '../services/ai.service';
import './AiChat.css';
import Modal from '../components/Modal';

const AiChat: React.FC = () => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recording, setRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const [showClearModal, setShowClearModal] = useState(false);
  const [expandedDetails, setExpandedDetails] = useState<{[id: number]: boolean}>({});

  useEffect(() => {
    aiService.getChatHistoryWithAssessments().then(setHistory).catch(() => setHistory([]));
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  // Función para obtener el color del nivel de riesgo
  const getRiskLevelColor = (riskLevel?: string) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low': return '#4CAF50';
      case 'moderate': return '#FF9800';
      case 'high': return '#F44336';
      case 'critical': return '#9C27B0';
      default: return 'transparent';
    }
  };

  // Explicaciones amigables para categorías
  const categoryDescriptions: Record<string, string> = {
    // Depresión
    estado_animo: 'Estado de ánimo bajo, tristeza o desesperanza',
    interés: 'Falta de interés o motivación en actividades',
    sueño: 'Problemas para dormir o cambios en el sueño',
    apetito: 'Cambios en el apetito o el peso',
    pensamientos: 'Pensamientos negativos, de inutilidad o muerte',
    // Ansiedad
    preocupación: 'Preocupación excesiva o miedo',
    físicos: 'Síntomas físicos (palpitaciones, sudoración, etc.)',
    cognitivos: 'Dificultad para concentrarse o pensamientos intrusivos',
    conductuales: 'Cambios en el comportamiento o evitación',
    // Estrés
    emocionales: 'Irritabilidad, frustración o ansiedad',
    // Bienestar
    físico: 'Salud física y energía',
    emocional: 'Bienestar emocional y autoestima',
    social: 'Relaciones y apoyo social',
    ocupacional: 'Satisfacción con trabajo o estudios',
  };

  // Diccionarios de traducción
  const typeTranslations: Record<string, string> = {
    stress: 'Estrés',
    anxiety: 'Ansiedad',
    depression: 'Depresión',
    crisis: 'Crisis',
  };
  const riskLevelTranslations: Record<string, string> = {
    low: 'Bajo',
    moderate: 'Moderado',
    high: 'Alto',
    critical: 'Crítico',
  };

  // Panel desplegable de detalles por mensaje
  const toggleDetails = (id: number) => {
    setExpandedDetails(prev => ({ ...prev, [id]: !prev[id] }));
  };

  // Función para mostrar la evaluación
  const renderAssessment = (assessment?: Assessment, msgId?: number) => {
    if (!assessment) return null;
    if (!assessment.type || !assessment.risk_level) return null;
    const riskColor = getRiskLevelColor(assessment.risk_level);
    // Render detalle específico
    const renderDetail = () => {
      if (assessment.depression_assessment) {
        const a = assessment.depression_assessment;
        return (
          <div className="assessment-detail">
            <h4>Evaluación de Depresión</h4>
            <p><strong>Puntaje:</strong> {a.score}</p>
            <ul>
              {Object.entries(a.categories).map(([cat, val]) => val > 0 && (
                <li key={cat}>
                  <strong>{categoryDescriptions[cat] || cat}:</strong> {val} <span style={{color:'#F44336', fontWeight:'bold'}}>{val >= 2 ? ' (Afectación importante)' : ' (Afectación leve)'}</span>
                </li>
              ))}
            </ul>
            {a.score === 0 && <p style={{color:'#4CAF50'}}>No se detectaron síntomas relevantes de depresión en tu mensaje.</p>}
            {a.score > 0 && <p style={{color:'#FF9800'}}>Se detectaron señales de depresión en las áreas resaltadas. Si estos síntomas persisten, considera hablar con un profesional.</p>}
          </div>
        );
      }
      if (assessment.anxiety_assessment) {
        const a = assessment.anxiety_assessment;
        return (
          <div className="assessment-detail">
            <h4>Evaluación de Ansiedad</h4>
            <p><strong>Puntaje:</strong> {a.score}</p>
            <ul>
              {Object.entries(a.categories).map(([cat, val]) => val > 0 && (
                <li key={cat}>
                  <strong>{categoryDescriptions[cat] || cat}:</strong> {val} <span style={{color:'#F44336', fontWeight:'bold'}}>{val >= 2 ? ' (Afectación importante)' : ' (Afectación leve)'}</span>
                </li>
              ))}
            </ul>
            {a.score === 0 && <p style={{color:'#4CAF50'}}>No se detectaron síntomas relevantes de ansiedad en tu mensaje.</p>}
            {a.score > 0 && <p style={{color:'#FF9800'}}>Se detectaron señales de ansiedad en las áreas resaltadas. Si estos síntomas persisten o interfieren con tu vida diaria, considera buscar apoyo profesional.</p>}
          </div>
        );
      }
      if (assessment.stress_assessment) {
        const a = assessment.stress_assessment;
        return (
          <div className="assessment-detail">
            <h4>Evaluación de Estrés</h4>
            <p><strong>Puntaje:</strong> {a.score}</p>
            <ul>
              {Object.entries(a.categories).map(([cat, val]) => val > 0 && (
                <li key={cat}>
                  <strong>{categoryDescriptions[cat] || cat}:</strong> {val} <span style={{color:'#F44336', fontWeight:'bold'}}>{val >= 2 ? ' (Afectación importante)' : ' (Afectación leve)'}</span>
                </li>
              ))}
            </ul>
            {a.score === 0 && <p style={{color:'#4CAF50'}}>No se detectaron síntomas relevantes de estrés en tu mensaje.</p>}
            {a.score > 0 && <p style={{color:'#FF9800'}}>Se detectaron señales de estrés en las áreas resaltadas. Si el estrés es persistente, prueba técnicas de relajación o busca apoyo.</p>}
          </div>
        );
      }
      if (assessment.crisis_indicators) {
        const c = assessment.crisis_indicators;
        return (
          <div className="assessment-detail crisis-detail" style={{border:'2px solid #F44336', background:'#fff3f3', borderRadius:'8px', padding:'12px', marginTop:'8px'}}>
            <h4 style={{color:'#F44336'}}>⚠️ Crisis detectada</h4>
            <ul style={{marginBottom:'8px'}}>
              {c.suicidal_ideation && <li><strong>Ideación suicida:</strong> Se detectaron frases relacionadas con pensamientos suicidas.</li>}
              {c.self_harm && <li><strong>Autolesión:</strong> Se detectaron frases relacionadas con autolesiones.</li>}
              {c.panic_attack && <li><strong>Ataque de pánico:</strong> Se detectaron síntomas de pánico o dificultad para respirar.</li>}
            </ul>
            <p style={{color:'#F44336', fontWeight:'bold'}}>Por favor, busca ayuda profesional o llama a los servicios de emergencia. Tu seguridad es lo más importante.</p>
          </div>
        );
      }
      return null;
    };
    const typeLabel = typeTranslations[assessment.type] || assessment.type;
    const riskLabel = riskLevelTranslations[assessment.risk_level] || assessment.risk_level;
    return (
      <div className="assessment-card" style={{ borderLeft: `4px solid ${riskColor}` }}>
        <div className="assessment-header">
          <span className="assessment-type">{typeLabel.toUpperCase()}</span>
          <span className="risk-level" style={{ backgroundColor: riskColor }}>
            {riskLabel.toUpperCase()}
          </span>
        </div>
        <div className="assessment-details">
          <p><strong>Evaluación:</strong> {typeLabel}</p>
          <p><strong>Nivel de riesgo:</strong> {riskLabel}</p>
          <p><strong>Fecha:</strong> {new Date(assessment.timestamp).toLocaleString()}</p>
        </div>
        {typeof msgId === 'number' && (
          <button
            className="toggle-details-btn"
            onClick={() => toggleDetails(msgId)}
            style={{margin:'8px 0', padding:'4px 12px', borderRadius:'6px', background:'#169ccf', color:'#fff', border:'none', cursor:'pointer'}}
          >
            {expandedDetails[msgId] ? 'Ocultar detalles' : 'Más detalles'}
          </button>
        )}
        {typeof msgId === 'number' && expandedDetails[msgId] && renderDetail()}
      </div>
    );
  };

  // Enviar texto
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await aiService.processText(input, sessionId || undefined);
      setSessionId(res.session_id);
      
      const newMessage: ChatMessage = {
        id: Date.now(),
        message: input,
        response: res.output,
        created_at: new Date().toISOString(),
        assessment: res.assessment,
        risk_level: res.risk_level
      };
      
      setHistory(h => [...h, newMessage]);
      setInput('');
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError('Error inesperado');
    } finally {
      setLoading(false);
    }
  };

  // Grabar audio
  const handleRecord = async () => {
    if (recording) {
      mediaRecorderRef.current?.stop();
      setRecording(false);
    } else {
      setError(null);
      setAudioUrl(null);
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new window.MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunks.current = [];
        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) audioChunks.current.push(e.data);
        };
        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
          const url = URL.createObjectURL(audioBlob);
          setAudioUrl(url);
        };
        mediaRecorder.start();
        setRecording(true);
      } catch {
        setError('No se pudo acceder al micrófono');
      }
    }
  };

  // Enviar audio grabado
  const handleSendAudio = async () => {
    if (!audioUrl) return;
    setLoading(true);
    setError(null);
    try {
      const audioBlob = await fetch(audioUrl).then(r => r.blob());
      const file = new File([audioBlob], 'nota-voz.webm', { type: 'audio/webm' });
      const res = await aiService.processVoice(file, sessionId || undefined);
      setSessionId(res.session_id);
      const newMessage: ChatMessage = {
        id: Date.now(),
        message: '', // No texto, solo audio
        response: res.output,
        created_at: new Date().toISOString(),
        assessment: res.assessment,
        risk_level: res.risk_level,
        audio_path: audioUrl, // Usar la URL local para previsualización inmediata
        message_type: 'audio'
      };
      setHistory(h => [...h, newMessage]);
      setAudioUrl(null);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError('Error inesperado');
    } finally {
      setLoading(false);
    }
  };

  // Limpiar conversación
  const handleClearConversation = async () => {
    setShowClearModal(true);
  };

  const confirmClearConversation = async () => {
    setShowClearModal(false);
    try {
      await aiService.clearConversation();
      setHistory([]);
      setSessionId(null);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError('Error al limpiar la conversación');
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2 className="chat-title">Chat con Feel Guard IA</h2>
        {history.length > 0 && (
          <button 
            onClick={handleClearConversation} 
            className="clear-btn"
            title="Limpiar conversación"
          >
            🗑️ Limpiar
          </button>
        )}
      </div>
      
      <div className="chat-history">
        {history.map((item, idx) => (
          <div key={item.id + '-' + idx} className="chat-bubble-group">
            <div className="chat-bubble user">
              {item.message_type === 'audio' && item.audio_path ? (
                <audio
                  src={item.audio_path.startsWith('blob:')
                    ? item.audio_path
                    : item.audio_path.startsWith('http')
                      ? item.audio_path
                      : `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/${item.audio_path.replace(/^\/+/, '')}`}
                  controls
                  style={{ width: '100%' }}
                />
              ) : (
                <span>{item.message}</span>
              )}
              <div className="chat-time">
                {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
            <div className="chat-bubble gpt">
              <span>{item.response}</span>
              {/* {item.risk_level && (
                <div className="risk-indicator" style={{ backgroundColor: getRiskLevelColor(item.risk_level) }}>
                  Riesgo: {item.risk_level.toUpperCase()}
                </div>
              )} */}
            </div>
            {item.assessment && (
              <div className="assessment-container">
                {renderAssessment(item.assessment, item.id)}
              </div>
            )}
          </div>
        ))}
        {/* Indicador de que la IA está escribiendo */}
        {loading && (
          <div className="chat-bubble-group">
            <div className="chat-bubble gpt">
              <span className="typing-indicator">La IA está escribiendo<span className="dot">.</span><span className="dot">.</span><span className="dot">.</span></span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>
      
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <textarea
          className="chat-input"
          value={input}
          onChange={e => setInput(e.target.value)}
          rows={2}
          placeholder="Escribe un mensaje..."
          disabled={loading}
        />
        <button type="submit" className="send-btn" disabled={loading || !input.trim()} title="Enviar texto">
          <span role="img" aria-label="Enviar">➤</span>
        </button>
        <button 
          type="button" 
          className={`audio-btn${recording ? ' recording' : ''}`} 
          onClick={handleRecord} 
          disabled={loading} 
          title={recording ? 'Detener grabación' : 'Grabar nota de voz'}
        >
          <span role="img" aria-label="Audio">🎤</span>
        </button>
      </form>
      
      {audioUrl && (
        <div className="audio-preview">
          <audio src={audioUrl} controls style={{ width: '100%' }} />
          <button onClick={handleSendAudio} className="send-audio-btn" disabled={loading}>
            <span role="img" aria-label="Enviar audio">Enviar audio</span>
          </button>
        </div>
      )}
      
      {error && <div className="chat-error">{error}</div>}

      <Modal
        open={showClearModal}
        onClose={() => setShowClearModal(false)}
        onConfirm={confirmClearConversation}
        title="Limpiar conversación"
        confirmText="Sí, limpiar"
        cancelText="Cancelar"
      >
        ¿Estás seguro de que quieres limpiar toda la conversación?
      </Modal>
    </div>
  );
};

export default AiChat; 