import React, { useEffect, useState } from 'react'
import { Routes, Route, Link, useNavigate } from 'react-router-dom'
import Login from './pages/Login'
import Projects from './pages/Projects'
import Defects from './pages/Defects'
import Reports from './pages/Reports'
import { setToken, getToken } from './api'

export default function App() {
  const [user, setUser] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    const t = getToken()
    if (!t) navigate('/login')
  }, [])

  const logout = () => {
    setToken(null); setUser(null); navigate('/login')
  }

  return (
    <div style={{fontFamily:'system-ui', padding:16}}>
      <h2>Defects Control Center</h2>
      <nav style={{display:'flex', gap:12, marginBottom:12}}>
        <Link to="/projects">Проекты</Link>
        <Link to="/defects">Дефекты</Link>
        <Link to="/reports">Отчёты</Link>
        <span style={{marginLeft:'auto'}}>
          {user?.email ? <>[{user.email}] <button onClick={logout}>Выйти</button></> : <Link to="/login">Войти</Link>}
        </span>
      </nav>
      <Routes>
        <Route path="/login" element={<Login onLogin={setUser} />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/defects" element={<Defects />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="*" element={<div>Открой «Проекты» или «Дефекты»</div>} />
      </Routes>
    </div>
  )
}
