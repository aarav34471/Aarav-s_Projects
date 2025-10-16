import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import { API } from '../constants';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  // 1) Keep the backend-provided user object
  const [user, setUser] = useState(null);

  // 2) Keep the raw JWT access token
  const [token, setToken] = useState(
    localStorage.getItem('accessToken') || ''
  );

  // 3) Any time the token changes, decode it to check expiry
  useEffect(() => {
    if (!token) return;

    const { exp } = jwtDecode(token);
    const hasExpired = Date.now() > exp * 1000;

    if (hasExpired) {
      logout();
    } else {
      // set axios header so all requests carry the token
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, [token]);

  // 4) login(): call the backend, save token & user
  const login = async (username, password) => {

    const data ={
      username: username,
      password: password,
    }
    const res = await axios.post(`${API}login/`, data);
    const { access, user: userFromServer } = res.data;

    // save the token
    setToken(access);
    localStorage.setItem('accessToken', access);

    // save the user object (id, username, email, account_type)
    setUser(userFromServer);
  
  };

  // 5) logout(): clear everything
  const logout = () => {
    setUser(null);
    setToken('');
    localStorage.removeItem('accessToken');
    delete axios.defaults.headers.common['Authorization'];
  };

  // 6) This is what any child component can grab via useContext(AuthContext)
  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
