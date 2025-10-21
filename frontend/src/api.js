const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000'

let token = localStorage.getItem('token') || null
export function setToken(t){ token = t; if(!t) localStorage.removeItem('token'); else localStorage.setItem('token', t) }
export function getToken(){ return token }

export const api = {
  async login(email, password){
    const r = await fetch(`${API}/api/auth/login`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email,password})})
    if(!r.ok) throw new Error('login failed')
    return r.json()
  },
  async projects(){
    const r = await fetch(`${API}/api/projects`, {headers:{'Authorization': `Bearer ${token}`}})
    if(!r.ok) throw new Error('projects failed')
    return r.json()
  },
  async createProject(data){
    const r = await fetch(`${API}/api/projects`, {method:'POST', headers:{'Content-Type':'application/json','Authorization':`Bearer ${token}`}, body: JSON.stringify(data)})
    if(!r.ok) throw new Error('create project failed')
    return r.json()
  },
  async defects(params={}){
    const qs = new URLSearchParams(params).toString()
    const r = await fetch(`${API}/api/defects?${qs}`, {headers:{'Authorization':`Bearer ${token}`}})
    if(!r.ok) throw new Error('defects failed')
    return r.json()
  },
  async createDefect(data){
    const r = await fetch(`${API}/api/defects`, {method:'POST', headers:{'Content-Type':'application/json','Authorization':`Bearer ${token}`}, body: JSON.stringify(data)})
    if(!r.ok) throw new Error('create defect failed')
    return r.json()
  },
  async updateStatus(id, status){
    const r = await fetch(`${API}/api/defects/${id}/status`, {method:'PATCH', headers:{'Content-Type':'application/json','Authorization':`Bearer ${token}`}, body: JSON.stringify({status})})
    if(!r.ok) throw new Error('update status failed')
    return r.json()
  },
  async summary(){
    const r = await fetch(`${API}/api/reports/summary`, {headers:{'Authorization':`Bearer ${token}`}})
    if(!r.ok) throw new Error('summary failed')
    return r.json()
  },
}
