import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ROLES } from '../utils/role';

export default function PrivateRoute({ children, allowed = [] }) {
  const { user, loading } = useAuth();
  if (loading) return <p className="p-4">Загрузка…</p>;
  if (!user) return <Navigate to="/login" />;
  if (allowed.length && !allowed.includes(user.role))
    return <Navigate to="/dashboard" />;
  return children;
}