import React, { useState, useRef, useEffect } from 'react';
import type { ChatHistoryItem } from '../services/ai.service';
import { aiService } from '../services/ai.service';
import './AiChat.css';

const AiChat: React.FC = () => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recording, setRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [history, setHistory] = useState<ChatHistoryItem[]>([]);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    aiService.getChatHistory().then(setHistory).catch(() => setHistory([]));
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  // Enviar texto
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await aiService.processText(input);
      setHistory(h => [
        ...h,
        { id: Date.now(), message: input, response: res.output, created_at: new Date().toISOString() }
      ]);
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
      const res = await aiService.processVoice(file);
      setHistory(h => [
        ...h,
        { id: Date.now(), message: '[Nota de voz]', response: res.output, created_at: new Date().toISOString() }
      ]);
      setAudioUrl(null);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError('Error inesperado');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <h2 className="chat-title">Chat con Feel Guard IA</h2>
      <div className="chat-history">
        {history.map((item, idx) => (
          <div key={item.id + '-' + idx} className="chat-bubble-group">
            <div className="chat-bubble user">
              <span>{item.message}</span>
              <div className="chat-time">{new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
            <div className="chat-bubble gpt">
              <span>{item.response}</span>
            </div>
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
        <button type="button" className={`audio-btn${recording ? ' recording' : ''}`} onClick={handleRecord} disabled={loading} title={recording ? 'Detener grabación' : 'Grabar nota de voz'}>
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
    </div>
  );
};

export default AiChat; 