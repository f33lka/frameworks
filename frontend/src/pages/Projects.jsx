import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Projects(){
  const [items, setItems] = useState([])
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')

  const load = async () => setItems(await api.projects())
  useEffect(()=>{ load() }, [])

  const create = async () => {
    if(!name.trim()) return
    await api.createProject({name, description: desc})
    setName(''); setDesc(''); load()
  }

  return (
    <div>
      <h3>Проекты</h3>
      <div style={{display:'flex', gap:8, marginBottom:12}}>
        <input placeholder="Название" value={name} onChange={e=>setName(e.target.value)} />
        <input placeholder="Описание" value={desc} onChange={e=>setDesc(e.target.value)} />
        <button onClick={create}>Создать</button>
      </div>
      <ul>
        {items.map(p => <li key={p.id}>#{p.id} {p.name} — {p.description}</li>)}
      </ul>
    </div>
  )
}
