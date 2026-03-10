// src/components/SessionControls.js
import React, { useState } from 'react';
import { createRoom, joinRoom } from '../api/rooms';

const SessionControls = ({ onSessionJoined }) => {
  const [username, setUsername] = useState('');
  const [roomId, setRoomId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [mode, setMode] = useState('create'); // 'create' or 'join'

  const handleCreateRoom = async () => {
    if (!username.trim()) {
      setError('Введите ваше имя');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const room = await createRoom(username);
      console.log('✅ Room created:', room);
      onSessionJoined(room.id, username);
    } catch (err) {
      setError('Ошибка при создании комнаты. Проверьте подключение к серверу.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleJoinRoom = async () => {
    if (!username.trim()) {
      setError('Введите ваше имя');
      return;
    }
    if (!roomId.trim()) {
      setError('Введите ID комнаты');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const room = await joinRoom(roomId, username);
      console.log('✅ Room joined:', room);
      onSessionJoined(roomId, username);
    } catch (err) {
      if (err.response?.status === 404) {
        setError('Комната не найдена. Проверьте ID.');
      } else {
        setError('Ошибка при подключении к комнате.');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="session-controls">
      <h2>🎬 Кино Вместе</h2>

      <div className="mode-selector">
        <button
          className={`mode-btn ${mode === 'create' ? 'active' : ''}`}
          onClick={() => setMode('create')}
        >
          Создать комнату
        </button>
        <button
          className={`mode-btn ${mode === 'join' ? 'active' : ''}`}
          onClick={() => setMode('join')}
        >
          Присоединиться
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="input-group">
        <label>Ваше имя:</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Введите ваше имя"
          disabled={loading}
        />
      </div>

      {mode === 'join' && (
        <div className="input-group">
          <label>ID комнаты:</label>
          <input
            type="text"
            value={roomId}
            onChange={(e) => setRoomId(e.target.value.toUpperCase())}
            placeholder="Например: ABC123"
            disabled={loading}
          />
        </div>
      )}

      <button
        className={`action-btn ${mode === 'create' ? 'create-btn' : 'join-btn'}`}
        onClick={mode === 'create' ? handleCreateRoom : handleJoinRoom}
        disabled={loading}
      >
        {loading ? 'Подключение...' : mode === 'create' ? 'Создать комнату' : 'Присоединиться'}
      </button>
    </div>
  );
};

export default SessionControls;