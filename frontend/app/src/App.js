// src/App.js
import React, { useState, useEffect } from 'react';
import './App.css';
import VideoPlayer from './components/VideoPlayer';
import Chat from './components/Chat';
import SessionControls from './components/SessionControls';
// Выберите один из вариантов:
//import socketManager from './utils/socket'; // для socket.io
 import socketManager from './utils/nativeSocket'; // для нативного WebSocket

function App() {
  const [sessionId, setSessionId] = useState('');
  const [username, setUsername] = useState('');
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const savedUsername = localStorage.getItem('kino-vmeste-username');
    if (savedUsername) {
      setUsername(savedUsername);
    } else {
      const randomUsername = `Зритель_${Math.floor(Math.random() * 1000)}`;
      setUsername(randomUsername);
    }

    // Проверяем статус WebSocket каждую секунду
    const checkConnection = setInterval(() => {
      setConnected(socketManager.isConnected());
    }, 1000);

    return () => clearInterval(checkConnection);
  }, []);

  const handleSessionJoined = (newSessionId, userUsername) => {
    localStorage.setItem('kino-vmeste-username', userUsername);

    // Подключаемся к WebSocket
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
        {!sessionId ? (
          <SessionControls onSessionJoined={handleSessionJoined} />
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