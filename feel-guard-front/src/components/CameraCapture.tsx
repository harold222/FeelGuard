import React, { useRef, useEffect, useState } from 'react';

interface CameraCaptureProps {
  onCapture: (file: File, previewUrl: string) => void;
  onCancel: () => void;
}

const CameraCapture: React.FC<CameraCaptureProps> = ({ onCapture, onCancel }) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const s = await navigator.mediaDevices.getUserMedia({ video: true });
        setStream(s);
        if (videoRef.current) {
          videoRef.current.srcObject = s;
        }
      } catch {
        setError('No se pudo acceder a la cámara');
      }
    })();
    return () => {
      stream?.getTracks().forEach(track => track.stop());
    };
    // eslint-disable-next-line
  }, []);

  const handleCapture = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      canvas.toBlob(blob => {
        if (blob) {
          const file = new File([blob], 'captured-image.png', { type: 'image/png' });
          const previewUrl = URL.createObjectURL(blob);
          onCapture(file, previewUrl);
        }
      }, 'image/png');
    }
  };

  return (
    <div style={{textAlign:'center', padding:24}}>
      <h3>Tomar foto</h3>
      {error ? (
        <div style={{color:'#f44336', marginBottom:16}}>{error}</div>
      ) : (
        <>
          <video ref={videoRef} autoPlay playsInline style={{ width: '100%', maxWidth: 320, borderRadius: 8 }} />
          <canvas ref={canvasRef} style={{ display: 'none' }} />
          <div style={{marginTop:16, display:'flex', justifyContent:'center', gap:12}}>
            <button className="send-audio-btn" onClick={handleCapture}>Capturar</button>
            <button className="send-audio-btn" style={{background:'#f44336'}} onClick={onCancel}>Cancelar</button>
          </div>
        </>
      )}
    </div>
  );
};

export default CameraCapture; 