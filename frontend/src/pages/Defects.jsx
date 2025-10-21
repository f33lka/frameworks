import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Defects(){
  const [projects, setProjects] = useState([])
  const [items, setItems] = useState([])
  const [projectId, setProjectId] = useState('')
  const [title, setTitle] = useState('')
  const [priority, setPriority] = useState('medium')

  const load = async () => {
    const ps = await api.projects()
    setProjects(ps)
    setProjectId(ps?.[0]?.id || '')
    setItems(await api.defects({project_id: ps?.[0]?.id || ''}))
  }
  useEffect(()=>{ load() }, [])

  const reload = async (pid) => setItems(await api.defects({project_id: pid}))

  const create = async () => {
    if(!projectId || !title.trim()) return
    await api.createDefect({project_id: Number(projectId), title, priority})
    setTitle('')
    reload(projectId)
  }

  const move = async (id, status) => {
    await api.updateStatus(id, status)
    reload(projectId)
  }

  return (
    <div>
      <h3>Дефекты</h3>
      <div style={{display:'flex', gap:8, alignItems:'center'}}>
        <label>Проект:</label>
        <select value={projectId} onChange={e=>{setProjectId(e.target.value); reload(e.target.value)}}>
          {projects.map(p => <option value={p.id} key={p.id}>{p.name}</option>)}
        </select>
      </div>

      <div style={{display:'flex', gap:8, marginTop:8}}>
        <input placeholder="Заголовок" value={title} onChange={e=>setTitle(e.target.value)} />
        <select value={priority} onChange={e=>setPriority(e.target.value)}>
          <option>low</option><option>medium</option><option>high</option>
        </select>
        <button onClick={create}>Добавить</button>
      </div>

      <table border="1" cellPadding="6" style={{marginTop:12, borderCollapse:'collapse'}}>
        <thead><tr><th>ID</th><th>Заголовок</th><th>Приоритет</th><th>Статус</th><th>Действия</th></tr></thead>
        <tbody>
          {items.map(d => (
            <tr key={d.id}>
              <td>{d.id}</td>
              <td>{d.title}</td>
              <td>{d.priority}</td>
              <td>{d.status}</td>
              <td>
                {d.status==='new' && <button onClick={()=>move(d.id,'in_progress')}>В работу</button>}
                {d.status==='in_progress' && <button onClick={()=>move(d.id,'in_review')}>На проверку</button>}
                {d.status==='in_review' && <>
                  <button onClick={()=>move(d.id,'in_progress')}>Вернуть</button>
                  <button onClick={()=>move(d.id,'closed')}>Закрыть</button>
                </>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
