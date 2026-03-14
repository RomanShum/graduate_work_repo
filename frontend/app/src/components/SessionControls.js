import React, { useState, useEffect } from 'react';
import { createRoom, joinRoom, getFilms, getFriends } from '../api/rooms';

const SessionControls = ({ onSessionJoined, username }) => {
  const [roomId, setRoomId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [mode, setMode] = useState('create');
  const [films, setFilms] = useState([]);
  const [selectedFilmId, setSelectedFilmId] = useState('');
  const [friends, setFriends] = useState([]);

  useEffect(() => {
    const loadFilms = async () => {
      try {
        const data = await getFilms();
        setFilms(data);
        if (data.length > 0) {
          setSelectedFilmId(data[0].id);
        }
      } catch (e) {
        console.error(e);
        setError('Не удалось загрузить список фильмов');
      }
    };

    loadFilms();
  }, []);

  useEffect(() => {
    const loadFriends = async () => {
      try {
        const data = await getFriends(selectedFilmId || null);
        setFriends(data);
      } catch (e) {
        console.error(e);
      }
    };

    if (selectedFilmId) {
      loadFriends();
    }
  }, [selectedFilmId]);

  const handleCreateRoom = async () => {
    if (!selectedFilmId) {
      setError('Выберите фильм');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const room = await createRoom(selectedFilmId);
      onSessionJoined(room.id, username);
    } catch (err) {
      setError('Ошибка при создании комнаты. Проверьте подключение к серверу.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleJoinRoom = async () => {
    if (!roomId.trim()) {
      setError('Введите ID комнаты');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const room = await joinRoom(roomId);
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
        <label>Вы вошли как:</label>
        <div className="readonly-value">{username}</div>
      </div>

      {mode === 'create' && (
        <div className="input-group">
          <label>Фильм:</label>
          <select
            value={selectedFilmId}
            onChange={(e) => setSelectedFilmId(e.target.value)}
            disabled={loading || films.length === 0}
          >
            {films.map((film) => (
              <option key={film.id} value={film.id}>
                {film.title}
              </option>
            ))}
          </select>
        </div>
      )}

      {mode === 'create' && friends.length > 0 && (
        <div className="friends-list">
          <h3>Друзья</h3>
          <ul>
            {friends.map((friend) => (
              <li key={friend.id}>
                {friend.login}
                {friend.in_favorites && ' — В избранном'}
              </li>
            ))}
          </ul>
        </div>
      )}

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