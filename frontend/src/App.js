import React, { useEffect, useMemo, useState } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import theme from './theme';
import AppLayout from './components/AppLayout';
import Toaster from './components/Toaster';
import api from './api';

import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import MenuItem from '@mui/material/MenuItem';
import Divider from '@mui/material/Divider';
import Chip from '@mui/material/Chip';

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function App() {
    const [habits, setHabits] = useState([]);
    const [checkins, setCheckins] = useState([]);
    const [toast, setToast] = useState({open:false, msg:'', severity:'success'});

    const [newHabit, setNewHabit] = useState({ title:'', goal_per_week:5 });
    const [mark, setMark] = useState({ habit_id:'', day:'' });

    const load = async () => {
        const h = await api.get('/habits'); setHabits(h.data);
        const c = await api.get('/checkins'); setCheckins(c.data);
    };

    useEffect(()=>{ load(); }, []);

    const addHabit = async () => {
        if (!newHabit.title.trim()) return;

        await api.post('/habits', { ...newHabit, goal_per_week: Number(newHabit.goal_per_week) });

        setNewHabit({ title:'', goal_per_week:5 }); setToast({open:true, msg:'Привычка добавлена'}); load();
    };
    const addCheckin = async () => {
        if (!mark.habit_id) return;
        
        await api.post('/checkins', { ...mark });

        setMark({ habit_id:'', day:'' }); setToast({open:true, msg:'Отмечено'}); load();
    };

    const last14 = useMemo(()=>{
        const days = [];
        const today = new Date();

        for (let i=13;i>=0;i--) {
            const d = new Date(today); d.setDate(today.getDate()-i);
            const key = d.toISOString().slice(0,10);

            days.push({ day:key, count:0 });
        }
        checkins.forEach(c => {
            const idx = days.findIndex(x=>x.day===c.day);

            if (idx>=0) days[idx].count += 1;
        });

        return days;
    }, [checkins]);

    return (
        <ThemeProvider theme={theme}>
            <AppLayout title="Habit Tracker Lite" subtitle="Привычки и отметки по дням">
              <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                      <Paper sx={{ p:2 }}>
                          <Typography variant="h6">Привычки</Typography>

                          <Divider sx={{ my:1 }} />

                          <Box sx={{ display:'flex', gap:1, flexWrap:'wrap', mb:2 }}>
                              <TextField label="Название" value={newHabit.title} onChange={e=>setNewHabit({...newHabit, title:e.target.value})} />

                              <TextField label="Цель/неделю" value={newHabit.goal_per_week} onChange={e=>setNewHabit({...newHabit, goal_per_week:e.target.value})} />

                              <Button variant="contained" onClick={addHabit}>Добавить</Button>
                          </Box>
                          <Box sx={{ display:'flex', gap:1, flexWrap:'wrap' }}>
                              {habits.map(h => <Chip key={h.id} label={`${h.title} • ${h.goal_per_week}/нед`} />)}
                              {!habits.length && <Typography color="text.secondary">Пока пусто</Typography>}
                          </Box>
                      </Paper>
                  </Grid>
                  <Grid item xs={12} md={6}>
                      <Paper sx={{ p:2, height:360 }}>
                          <Typography variant="h6">Активность (14 дней)</Typography>

                          <ResponsiveContainer width="100%" height={300}>
                              <BarChart data={last14}>
                                  <CartesianGrid strokeDasharray="3 3" />

                                  <XAxis dataKey="day" />

                                  <YAxis allowDecimals={false} />

                                  <Tooltip />

                                  <Bar dataKey="count" />
                              </BarChart>
                          </ResponsiveContainer>
                      </Paper>
                  </Grid>
                  <Grid item xs={12}>
                      <Paper sx={{ p:2 }}>
                          <Typography variant="h6">Отметить выполнение</Typography>

                          <Divider sx={{ my:1 }} />

                          <Box sx={{ display:'flex', gap:1, flexWrap:'wrap', mb:2 }}>
                              <TextField select label="Привычка" value={mark.habit_id} onChange={e=>setMark({...mark, habit_id:Number(e.target.value)})} sx={{ minWidth:260 }}>
                                  {habits.map(h => <MenuItem key={h.id} value={h.id}>{h.title}</MenuItem>)}
                              </TextField>

                              <TextField label="Дата (YYYY-MM-DD)" value={mark.day} onChange={e=>setMark({...mark, day:e.target.value})} />

                              <Button variant="contained" onClick={addCheckin}>Отметить</Button>
                          </Box>

                          <Typography variant="subtitle2" color="text.secondary">Последние отметки</Typography>

                          {checkins.map(c => (
                              <Box key={c.id} sx={{ display:'flex', justifyContent:'space-between', py:0.5 }}>
                                  <Box>{c.day} — {c.habit}</Box>
                              </Box>
                          ))}
                      </Paper>
                  </Grid>
              </Grid>

              <Toaster open={toast.open} message={toast.msg} onClose={()=>setToast({...toast, open:false})} />
            </AppLayout>
        </ThemeProvider>
    );
}