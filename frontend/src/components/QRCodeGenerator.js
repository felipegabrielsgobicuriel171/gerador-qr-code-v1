import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './QRCodeGenerator.css';

function QRCodeGenerator() {
  const [qrData, setQrData] = useState('');
  const [qrImage, setQrImage] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const authToken = localStorage.getItem('authToken');
    if (!authToken) {
      navigate('/login');
      return;
    }

    const verifyToken = async () => {
      try {
        await axios.get('http://localhost:5000/verify_token', {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        });
        // Se a requisição for bem-sucedida (status 2xx), o token é válido.
      } catch (error) {
        // Se houver um erro (status 4xx ou 5xx), o token é inválido ou expirou.
        localStorage.removeItem('authToken');
        navigate('/login');
      }
    };

    verifyToken();
  }, [navigate]);

  const handleGenerateQRCode = async () => {
    if (!qrData.trim()) {
      setError('Por favor, insira algum dado.');
      setQrImage(null);
      return;
    }

    try {
      setLoading(true);
      setError('');
      const authToken = localStorage.getItem('authToken');
      const response = await axios.post(
        'http://localhost:5000/generate_qrcode',
        { data: qrData },
        {
          responseType: 'blob',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${authToken}`, // Envia o token para o backend
          },
        }
      );

      const imageUrl = URL.createObjectURL(response.data);
      setQrImage(imageUrl);
      setDownloadUrl(imageUrl);
    } catch (error) {
      setError(error.response?.data?.message || 'Erro ao gerar QR Code');
      setQrImage(null);
      setDownloadUrl(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="qr-container">
      <h2 className="qr-title">Gerador de QR Code</h2>
      <textarea
        className="qr-textarea"
        value={qrData}
        onChange={(e) => setQrData(e.target.value)}
        placeholder="Digite os dados"
      />
      <button className="glow-on-hover" onClick={handleGenerateQRCode} disabled={loading}>
        {loading ? 'Gerando...' : 'Gerar QR Code'}
      </button>

      {error && <p className="qr-error">{error}</p>}

      {qrImage && (
        <div className="qr-result">
          <img src={qrImage} alt="QR Code" className="qr-image" />
          <a href={downloadUrl} download="qrcode.png">
            <button className="glow-on-hover">Baixar QR Code</button>
          </a>
        </div>
      )}
    </div>
  );
}

export default QRCodeGenerator;