import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import './LoginForm.css';


function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/login', { username, password });

      console.log('Resposta completa do login:', response.data);

      if (response.data.token) {
        localStorage.setItem('authToken', response.data.token);
        navigate('/');
      } else {
        setError('Token de autenticação não retornado');
      }
    } catch (error) {
      setError(error.response?.data?.message || 'Erro ao fazer login');
    }
  };

  return (
    <div className="login-container">
      <div className="login-form">
        <h2>Login</h2>
        {error && <p className="error-message">{error}</p>}
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Usuário"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">Entrar</button>
        </form>
        <p>Não tem uma conta? <Link to="/register">Cadastre-se</Link></p>
      </div>
    </div>
  );
}

export default LoginForm;