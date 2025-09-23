import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { ROLES } from '../utils/role';

export default function Register() {
  const [form, setForm] = useState({
    email: '',
    password: '',
    full_name: '',
    role: ROLES.ENGINEER,
  });
  const { register } = useAuth();
  const nav = useNavigate();

  const handle = (e) => {
    e.preventDefault();
    register(form).then(() => nav('/dashboard'));
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form onSubmit={handle} className="bg-white p-6 rounded shadow-md w-96">
        <h2 className="text-xl font-bold mb-4">Регистрация</h2>
        <input
          className="input mb-3"
          placeholder="ФИО"
          required
          onChange={(e) => setForm({ ...form, full_name: e.target.value })}
        />
        <input
          className="input mb-3"
          placeholder="Email"
          required
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />
        <input
          className="input mb-3"
          type="password"
          placeholder="Пароль"
          required
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />
        <select
          className="input mb-3"
          value={form.role}
          onChange={(e) => setForm({ ...form, role: e.target.value })}
        >
          <option value={ROLES.ENGINEER}>Инженер</option>
          <option value={ROLES.MANAGER}>Менеджер</option>
          <option value={ROLES.OBSERVER}>Наблюдатель</option>
        </select>
        <button className="btn btn-primary w-full">Зарегистрироваться</button>
      </form>
    </div>
  );
}