import React, { useState, useRef, useEffect } from 'react';
import type { ChatMessage, Assessment, DepressionClassification } from '../types/ai';
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

  // Diccionarios de traducción
  const typeTranslations: Record<string, string> = {
    depression: 'Depresión',
    neutral: 'Neutral',
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
  const renderAssessment = (assessment?: Assessment, classification?: DepressionClassification, msgId?: number) => {
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
            <p><strong>Nivel:</strong> {a.level}</p>
            <p><strong>Puntaje:</strong> {a.score}</p>
            <p><strong>Es depresión:</strong> {a.is_depression ? 'Sí' : 'No'}</p>
            <p><strong>Probabilidad neutro:</strong> {(a.probability_neutral * 100).toFixed(1)}%</p>
            <p><strong>Probabilidad depresión:</strong> {(a.probability_depression * 100).toFixed(1)}%</p>
            
            {a.score === 0 && <p style={{color:'#4CAF50'}}>No se detectaron síntomas relevantes de depresión en tu mensaje.</p>}
            {a.score > 0 && <p style={{color:'#FF9800'}}>Se detectaron señales de depresión. Si estos síntomas persisten, considera hablar con un profesional.</p>}
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
        risk_level: res.risk_level,
        depression_classification: res.depression_classification
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
        depression_classification: res.depression_classification,
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
            </div>
            {item.assessment && (
              <div className="assessment-container">
                {renderAssessment(item.assessment, item.depression_classification, item.id)}
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