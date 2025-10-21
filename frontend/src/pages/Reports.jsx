import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Reports(){
  const [s, setS] = useState(null)
  useEffect(()=>{ api.summary().then(setS) }, [])
  if(!s) return <div>Загрузка...</div>
  return (
    <div>
      <h3>Сводка</h3>
      <p>Всего дефектов: <b>{s.total}</b></p>
      <h4>По статусам</h4>
      <ul>{Object.entries(s.by_status).map(([k,v]) => <li key={k}>{k}: {v}</li>)}</ul>
      <h4>По приоритетам</h4>
      <ul>{Object.entries(s.by_priority).map(([k,v]) => <li key={k}>{k}: {v}</li>)}</ul>
    </div>
  )
}
