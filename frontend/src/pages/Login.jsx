import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, setToken } from '../api'

export default function Login({onLogin}){
  const [email, setEmail] = useState('admin@example.com')
  const [password, setPassword] = useState('admin123')
  const [err, setErr] = useState(null)
  const nav = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    try{
      const data = await api.login(email,password)
      setToken(data.access_token)
      onLogin?.(data.user)
      nav('/projects')
    }catch(e){
      setErr('Неверный логин/пароль')
    }
  }

  return (
    <form onSubmit={submit} style={{display:'grid', gap:8, maxWidth:320}}>
      <h3>Вход</h3>
      <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="email" />
      <input value={password} onChange={e=>setPassword(e.target.value)} type="password" placeholder="password" />
      <button>Войти</button>
      {err && <div style={{color:'crimson'}}>{err}</div>}
      <p>demo: admin@example.com / admin123</p>
    </form>
  )
}
