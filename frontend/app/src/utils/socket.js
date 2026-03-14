import { io } from 'socket.io-client';

const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'http://localhost:8000';

class SocketManager {
  constructor() {
    this.socket = null;
    this.roomId = null;
    this.username = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
  }

  connect(roomId, username) {
    if (this.socket) {
      this.disconnect();
    }

    this.roomId = roomId;
    this.username = username;

    this.socket = io(`${SOCKET_URL}/ws/${roomId}/${username}`, {
      path: '/ws',
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 1000,
      timeout: 10000,
      forceNew: true
    });

    this.socket.on('connect', () => {
      this.reconnectAttempts = 0;
    });

    this.socket.on('connect_error', (error) => {
      this.reconnectAttempts++;
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
    });

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    this.socket.onAny((event, data) => {
      console.log('WebSocket received:', event, data);
      this.handleEvent(event, data);
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      console.log('WebSocket disconnected');
    }

    this.roomId = null;
    this.username = null;
    this.listeners.clear();
    this.reconnectAttempts = 0;
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

  emit(event, data) {
    if (this.socket && this.socket.connected) {
      this.socket.emit(event, data);
      console.log('WebSocket sent:', event, data);
    } else {
      console.warn('Cannot emit, socket not connected');
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
    return this.socket?.connected || false;
  }

  getSocketId() {
    return this.socket?.id || null;
  }
}

const socketManager = new SocketManager();
export default socketManager;