// frontend/src/App.tsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import { Dashboard } from './pages/Dashboard';

// Secure Session Interceptor Matrix Guard
const ProtectedRoute = ({ children }: { children: React.JSX.Element }) => {
  const token = localStorage.getItem('raptor_token');

  if (!token) {
    // Session token context missing -> kick operator back to gateway interface
    return <Navigate to="/login" replace />;
  }

  return children;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Entry-Point Matrix Handshake Boundary */}
        <Route path="/login" element={<Login />} />

        {/* Operational Protected Diagnostics Dashboards */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Dynamic Fallback Redirection Strategy */}
        <Route
          path="*"
          element={
            localStorage.getItem('raptor_token')
              ? <Navigate to="/dashboard" replace />
              : <Navigate to="/login" replace />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
