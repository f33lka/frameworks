import { createContext, useContext, useEffect, useState } from 'react';
import api from '../api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const login = async (email, password) => {
    const { data } = await api.post('/login', { email, password });
    localStorage.setItem('token', data.access_token);
    setUser(data.user);
  };

  const register = async (body) => {
    await api.post('/register', body);
    return login(body.email, body.password);
  };

  const logout = () => {
    localStorage.clear();
    setUser(null);
    window.location = '/login';
  };

  useEffect(() => {
    api
      .get('/me')
      .then((r) => setUser(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};