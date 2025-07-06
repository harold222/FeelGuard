import React from 'react';
import './Modal.css';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  onConfirm?: () => void;
  title?: string;
  children: React.ReactNode;
  confirmText?: string;
  cancelText?: string;
}

const Modal: React.FC<ModalProps> = ({ open, onClose, onConfirm, title, children, confirmText = 'Aceptar', cancelText = 'Cancelar' }) => {
  if (!open) return null;
  return (
    <div className="modal-backdrop">
      <div className="modal-content">
        {title && <h3 className="modal-title">{title}</h3>}
        <div className="modal-body">{children}</div>
        <div className="modal-actions">
          <button className="modal-btn cancel" onClick={onClose}>{cancelText}</button>
          {onConfirm && <button className="modal-btn confirm" onClick={onConfirm}>{confirmText}</button>}
        </div>
      </div>
    </div>
  );
};

export default Modal; 