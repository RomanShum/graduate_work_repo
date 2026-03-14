import apiClient from './client';

export const createSession = async (username) => {
  try {

    const response = await apiClient.post('/api/rooms', null, {
      params: { creator: username }
    });

    return response.data;
  } catch (error) {
    throw error;
  }
};