// api/session.js
import apiClient from './client';

export const createSession = async (username) => {
  try {
    console.log('📝 Creating room for user:', username);
    console.log('Sending request to:', `/api/rooms?creator=${username}`);

    const response = await apiClient.post('/api/rooms', null, {
      params: { creator: username }
    });

    console.log('✅ Room created successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Error in createSession:', error);
    throw error;
  }
};

// Остальные функции...