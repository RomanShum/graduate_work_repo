// src/components/Chat.js
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { sendChatMessage, getChatHistory } from '../api/rooms';
import socketManager from '../utils/nativeSocket'; // Импортируем нативный менеджер

const Chat = ({ sessionId, username }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [users, setUsers] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef(null);

  // Загрузка истории чата
  const loadChatHistory = useCallback(async () => {
    try {
      console.log('Loading chat history for room:', sessionId);
      const history = await getChatHistory(sessionId);
      console.log('Chat history loaded:', history.length, 'messages');
      setMessages(history);
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  }, [sessionId]);

  // Обработка нового сообщения через WebSocket
  const handleNewMessage = useCallback((data) => {
    console.log('📨 New message via WebSocket:', data);
    setMessages(prev => {
      // Проверяем, нет ли уже такого сообщения (чтобы избежать дубликатов)
      const exists = prev.some(m =>
        m.timestamp === data.timestamp &&
        m.username === data.username &&
        m.message === data.message
      );

      if (exists) {
        console.log('Message already exists, skipping');
        return prev;
      }

      return [...prev, {
        username: data.username,
        message: data.message,
        timestamp: data.timestamp || new Date().toISOString()
      }];
    });
  }, []);

  // Обработка подключения пользователя
  const handleUserJoined = useCallback((data) => {
    console.log('👤 User joined:', data);
    setMessages(prev => [...prev, {
      username: 'system',
      message: `👋 ${data.username} присоединился к комнате`,
      timestamp: data.timestamp
    }]);
    setUsers(prev => [...prev, data.username]);
  }, []);

  // Обработка отключения пользователя
  const handleUserLeft = useCallback((data) => {
    console.log('👋 User left:', data);
    setMessages(prev => [...prev, {
      username: 'system',
      message: `👋 ${data.username} покинул комнату`,
      timestamp: data.timestamp
    }]);
    setUsers(prev => prev.filter(u => u !== data.username));
  }, []);

  // Обработка подтверждения подключения
  const handleConnectionEstablished = useCallback((data) => {
    console.log('🔌 Connection established:', data);
    setIsConnected(true);
    setMessages(prev => [...prev, {
      username: 'system',
      message: '✅ Подключение к чату установлено',
      timestamp: data.timestamp
    }]);
  }, []);

  // Обработка изменения состояния подключения
  const handleConnectionChanged = useCallback((data) => {
    console.log('🔌 Connection changed:', data);
    setIsConnected(data.connected);
  }, []);

  useEffect(() => {
    console.log('Chat component mounted for room:', sessionId);

    // Загружаем историю
    loadChatHistory();

    // Подписываемся на события WebSocket
    socketManager.on('connection_established', handleConnectionEstablished);
    socketManager.on('connection_changed', handleConnectionChanged);
    socketManager.on('chat', handleNewMessage);
    socketManager.on('user_joined', handleUserJoined);
    socketManager.on('user_left', handleUserLeft);

    // Проверяем текущий статус
    const connected = socketManager.isConnected();
    console.log('WebSocket connected:', connected);
    setIsConnected(connected);

    return () => {
      // Отписываемся от событий
      socketManager.off('connection_established', handleConnectionEstablished);
      socketManager.off('connection_changed', handleConnectionChanged);
      socketManager.off('chat', handleNewMessage);
      socketManager.off('user_joined', handleUserJoined);
      socketManager.off('user_left', handleUserLeft);
    };
  }, [sessionId, loadChatHistory, handleConnectionEstablished, handleConnectionChanged, handleNewMessage, handleUserJoined, handleUserLeft]);

  // Скролл к последнему сообщению
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const messageText = inputMessage.trim();
    console.log('Sending message:', messageText);

    try {
      // 1. Отправляем через HTTP для сохранения в истории
      const savedMessage = await sendChatMessage(sessionId, username, messageText);
      console.log('Message saved via HTTP:', savedMessage);

      // 2. Отправляем через WebSocket для real-time
      const wsConnected = socketManager.isConnected();
      console.log('WebSocket connected for sending:', wsConnected);

      if (wsConnected) {
        const sent = socketManager.send({
          type: 'chat',
          message: messageText
        });
        console.log('Message sent via WebSocket:', sent);
      } else {
        console.warn('WebSocket not connected, adding message locally');
        // Добавляем сообщение локально
        setMessages(prev => [...prev, {
          username: username,
          message: messageText,
          timestamp: new Date().toISOString()
        }]);
      }

      setInputMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h3>💬 Чат комнаты</h3>
        <div className="users-count">
          👥 {users.length + 1}
          <span className={`status-dot-small ${isConnected ? 'connected' : 'disconnected'}`} />
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="no-messages">
            Нет сообщений. Напишите что-нибудь!
          </div>
        )}

        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${
              msg.username === 'system' ? 'system' :
              msg.username === username ? 'own' : 'other'
            }`}
          >
            {msg.username !== 'system' && (
              <span className="message-username">
                {msg.username === username ? 'Вы' : msg.username}:
              </span>
            )}
            <span className="message-text">{msg.message}</span>
            <span className="message-time">{formatTime(msg.timestamp)}</span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Введите сообщение..."
        />
        <button
          onClick={sendMessage}
          disabled={!inputMessage.trim()}
        >
          Отправить
        </button>
      </div>

      {!isConnected && (
        <div className="connection-warning">
          ⚠️ Подключение к чату в реальном времени отсутствует.
          Сообщения будут видны только вам.
        </div>
      )}
    </div>
  );
};

export default Chat;