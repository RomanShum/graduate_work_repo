// src/utils/nativeSocket.js
class NativeWebSocketManager {
  constructor() {
    this.ws = null;
    this.roomId = null;
    this.username = null;
    this.listeners = new Map();
    this.reconnectTimeout = null;
    this.connectionState = 'disconnected'; // 'connecting', 'connected', 'disconnected'
  }

  connect(roomId, username) {
    if (this.ws) {
      this.disconnect();
    }

    this.roomId = roomId;
    this.username = username;
    this.connectionState = 'connecting';

    const token = localStorage.getItem('access_token');
    const query = token ? `?token=${encodeURIComponent(token)}` : '';
    const wsUrl = `ws://localhost:8000/ws/${roomId}/${username}${query}`;
    console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('✅ WebSocket connected');
      this.connectionState = 'connected';

      // Уведомляем всех слушателей о подключении
      this.handleEvent('connection_changed', { connected: true });

      // Отправляем приветственное сообщение
      this.send({
        type: 'ping',
        timestamp: Date.now()
      });
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📨 WebSocket received:', data);
        this.handleEvent(data.type, data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      this.connectionState = 'error';
      this.handleEvent('connection_error', error);
    };

    this.ws.onclose = () => {
      console.log('📴 WebSocket disconnected');
      this.connectionState = 'disconnected';
      this.handleEvent('connection_changed', { connected: false });

      // Пытаемся переподключиться через 3 секунды
      if (this.reconnectTimeout) {
        clearTimeout(this.reconnectTimeout);
      }
      this.reconnectTimeout = setTimeout(() => {
        if (this.roomId && this.username && this.connectionState !== 'connected') {
          console.log('🔄 Reconnecting...');
          this.connect(this.roomId, this.username);
        }
      }, 3000);
    };

    return this.ws;
  }

  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.roomId = null;
    this.username = null;
    this.connectionState = 'disconnected';
    this.listeners.clear();
    console.log('🔌 WebSocket disconnected');
    this.handleEvent('connection_changed', { connected: false });
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
      console.log('📤 WebSocket sent:', data);
      return true;
    } else {
      console.warn('⚠️ Cannot send, WebSocket not connected. State:', this.ws?.readyState);
      return false;
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback);
    }
  }

  handleEvent(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in ${event} handler:`, error);
        }
      });
    }
  }

  isConnected() {
    // Проверяем реальное состояние WebSocket
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  getState() {
    return this.connectionState;
  }

  getSocketId() {
    return 'ws-' + Date.now(); // Заглушка, т.к. нативный WebSocket не дает ID
  }
}

const nativeSocketManager = new NativeWebSocketManager();
export default nativeSocketManager;