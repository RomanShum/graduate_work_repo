// src/api/rooms.js
import apiClient from './client';

export const createRoom = async (filmId) => {
  try {
    console.log('📝 Creating room for film:', filmId);
    const response = await apiClient.post('/api/rooms', null, {
      params: { film_id: filmId }
    });
    return response.data;
  } catch (error) {
    console.error('❌ Error creating room:', error);
    throw error;
  }
};

export const joinRoom = async (roomId) => {
  try {
    console.log('📝 Joining room:', roomId);
    const response = await apiClient.post(`/api/rooms/${roomId}/join`);
    return response.data;
  } catch (error) {
    console.error('❌ Error joining room:', error);
    throw error;
  }
};

export const leaveRoom = async (roomId) => {
  try {
    const response = await apiClient.post(`/api/rooms/${roomId}/leave`);
    return response.data;
  } catch (error) {
    console.error('❌ Error leaving room:', error);
    throw error;
  }
};

export const getRoom = async (roomId) => {
  try {
    const response = await apiClient.get(`/api/rooms/${roomId}`);
    return response.data;
  } catch (error) {
    console.error('❌ Error getting room:', error);
    throw error;
  }
};

export const getRoomUsers = async (roomId) => {
  try {
    const response = await apiClient.get(`/api/rooms/${roomId}/users`);
    return response.data;
  } catch (error) {
    console.error('❌ Error getting users:', error);
    return { users: [] };
  }
};

export const sendChatMessage = async (roomId, message) => {
  try {
    const response = await apiClient.post(`/api/rooms/${roomId}/chat`, null, {
      params: { message }
    });
    return response.data;
  } catch (error) {
    console.error('❌ Error sending message:', error);
    throw error;
  }
};

export const getChatHistory = async (roomId, limit = 50) => {
  try {
    const response = await apiClient.get(`/api/rooms/${roomId}/chat`, {
      params: { limit }
    });
    return response.data;
  } catch (error) {
    console.error('❌ Error getting chat history:', error);
    return [];
  }
};

export const videoAction = async (roomId, action, time) => {
  try {
    const response = await apiClient.post(`/api/rooms/${roomId}/video`, null, {
      params: { action, time }
    });
    return response.data;
  } catch (error) {
    console.error('❌ Error video action:', error);
    throw error;
  }
};

export const getVideoState = async (roomId) => {
  try {
    const response = await apiClient.get(`/api/rooms/${roomId}/video/state`);
    return response.data;
  } catch (error) {
    console.error('❌ Error getting video state:', error);
    return { is_playing: false, current_time: 0, video_url: '' };
  }
};

export const getFilms = async () => {
  try {
    const response = await apiClient.get('/api/rooms/films');
    return response.data;
  } catch (error) {
    console.error('❌ Error getting films:', error);
    return [];
  }
};

export const getFriends = async (filmId) => {
  try {
    const response = await apiClient.get('/api/rooms/friends', {
      params: filmId ? { film_id: filmId } : {},
    });
    return response.data;
  } catch (error) {
    console.error('❌ Error getting friends:', error);
    return [];
  }
};