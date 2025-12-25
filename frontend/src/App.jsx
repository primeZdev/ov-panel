import { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import DashboardLayout from './pages/DashboardLayout';
import ServerStats from './pages/ServerStats';
import UserManagement from './pages/UserManagement';
import NodeManagement from './pages/NodeManagement';
import AdminManagement from './pages/AdminManagement';

import favicon from './assets/fav.webp';

function App() {
  const { isAuthenticated, userRole } = useAuth();


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
        {userRole !== 'admin' && <Route path="nodes" element={<NodeManagement />} />}
        {userRole === 'main_admin' && <Route path="admins" element={<AdminManagement />} />}
      </Route>
      <Route path="*" element={<Navigate to={isAuthenticated ? "/" : "/login"} />} />
    </Routes>
  );
}

export default App;