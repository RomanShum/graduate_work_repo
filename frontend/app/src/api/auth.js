import apiClient from './client';

export const login = async (login, password) => {
  const formData = new URLSearchParams();
  formData.append('username', login);
  formData.append('password', password);

  const response = await apiClient.post('/auth/v1/user/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  return response.data;
};

