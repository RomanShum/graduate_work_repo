import React, { useState, useEffect } from 'react';
import './App.css';
import VideoPlayer from './components/VideoPlayer';
import Chat from './components/Chat';
import SessionControls from './components/SessionControls';
import AuthForm from './components/AuthForm';
import socketManager from './utils/nativeSocket';

function App() {
  const [sessionId, setSessionId] = useState('');
  const [username, setUsername] = useState(localStorage.getItem('kino-vmeste-username') || '');
  const [connected, setConnected] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(
    !!localStorage.getItem('access_token')
  );

  useEffect(() => {
    const checkConnection = setInterval(() => {
      setConnected(socketManager.isConnected());
    }, 1000);

    return () => clearInterval(checkConnection);
  }, []);

  const handleLoginSuccess = ({ login }) => {
    setIsAuthenticated(true);
    setUsername(login);
  };

  const handleSessionJoined = (newSessionId, userUsername) => {
    localStorage.setItem('kino-vmeste-username', userUsername);

    socketManager.connect(newSessionId, userUsername);

    setSessionId(newSessionId);
    setUsername(userUsername);
  };

  const handleLeaveSession = () => {
    socketManager.disconnect();
    setSessionId('');
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎬 Кино Вместе</h1>
        <div className="connection-status">
          <span className={`status-dot ${connected ? 'connected' : 'disconnected'}`} />
          {connected ? 'WebSocket подключен' : 'WebSocket отключен'}
        </div>
      </header>

      <main className="app-main">
        {!isAuthenticated ? (
          <AuthForm onSuccess={handleLoginSuccess} />
        ) : !sessionId ? (
          <SessionControls
            onSessionJoined={handleSessionJoined}
            username={username}
          />
        ) : (
          <div className="room-container">
            <div className="room-header">
              <h2>Комната: {sessionId}</h2>
              <button onClick={handleLeaveSession} className="leave-button">
                Покинуть комнату
              </button>
            </div>

            <div className="content-wrapper">
              <div className="video-section">
                <VideoPlayer sessionId={sessionId} username={username} />
              </div>
              <div className="chat-section">
                <Chat sessionId={sessionId} username={username} />
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;