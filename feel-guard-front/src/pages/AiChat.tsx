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

  // Función para mostrar la evaluación
  const renderAssessment = (assessment?: Assessment) => {
    if (!assessment) return null;

    const riskColor = getRiskLevelColor(assessment.risk_level);
    
    return (
      <div className="assessment-card" style={{ borderLeft: `4px solid ${riskColor}` }}>
        <div className="assessment-header">
          <span className="assessment-type">{assessment.type.toUpperCase()}</span>
          <span className="risk-level" style={{ backgroundColor: riskColor }}>
            {assessment.risk_level.toUpperCase()}
          </span>
        </div>
        <div className="assessment-details">
          <p><strong>Evaluación:</strong> {assessment.type}</p>
          <p><strong>Nivel de riesgo:</strong> {assessment.risk_level}</p>
          <p><strong>Fecha:</strong> {new Date(assessment.timestamp).toLocaleString()}</p>
        </div>
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
        message: '[Nota de voz]',
        response: res.output,
        created_at: new Date().toISOString(),
        assessment: res.assessment,
        risk_level: res.risk_level
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
              <span>{item.message}</span>
              <div className="chat-time">
                {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
            <div className="chat-bubble gpt">
              <span>{item.response}</span>
              {item.risk_level && (
                <div className="risk-indicator" style={{ backgroundColor: getRiskLevelColor(item.risk_level) }}>
                  Riesgo: {item.risk_level.toUpperCase()}
                </div>
              )}
            </div>
            {item.assessment && (
              <div className="assessment-container">
                {renderAssessment(item.assessment)}
              </div>
            )}
          </div>
        ))}
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