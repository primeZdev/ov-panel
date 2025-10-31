import { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import DashboardLayout from './pages/DashboardLayout';
import ServerStats from './pages/ServerStats';
import UserManagement from './pages/UserManagement';
import NodeManagement from './pages/NodeManagement';
import SettingsPage from './pages/SettingsPage';

import favicon from './assets/fav.webp';

function App() {
  const { isAuthenticated } = useAuth();

  
  useEffect(() => {
    const link = document.createElement('link');
    link.rel = 'icon';
    link.type = 'image/webp';
    link.href = favicon;
    document.head.appendChild(link);

    return () => {
      document.head.removeChild(link);
    };
  }, []);

  return (
    <Routes>
      <Route 
        path="/login" 
        element={isAuthenticated ? <Navigate to="/" /> : <LoginPage />} 
      />
      <Route 
        path="/" 
        element={isAuthenticated ? <DashboardLayout /> : <Navigate to="/login" />}>
        <Route index element={<ServerStats />} />
        <Route path="users" element={<UserManagement />} />
        <Route path="nodes" element={<NodeManagement />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to={isAuthenticated ? "/" : "/login"} />} />
    </Routes>
  );
}

export default App;