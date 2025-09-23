import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  return (
    <nav className="bg-indigo-600 text-white px-4 py-3 flex items-center justify-between">
      <div className="font-bold">BuildDefectHub</div>
      <div className="flex gap-4 items-center">
        <span>{user.full_name}</span>
        <button onClick={logout} className="btn btn-sm btn-outline">
          Выйти
        </button>
      </div>
    </nav>
  );
}