import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import CssBaseline from '@mui/material/CssBaseline';

export default function AppLayout({ title, subtitle, actions, children }) {
    return (
        <Box sx={{ minHeight:'100vh',
            background:'radial-gradient(1200px 600px at 10% -10%, rgba(79,70,229,0.12), transparent), radial-gradient(900px 500px at 100% -10%, rgba(6,182,212,0.12), transparent)'}}>
            <CssBaseline />
            <AppBar position="sticky" color="inherit" sx={{ bgcolor:'background.paper' }}>
                <Toolbar sx={{ gap:2, py:1.5 }}>
                    <Box sx={{ width:10, height:10, borderRadius:'50%', bgcolor:'primary.main', boxShadow:2 }} />
                    <Typography variant="h6" color="primary" sx={{ fontWeight: 800 }}>{title}</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ ml:1, flexGrow:1 }}>{subtitle}</Typography>
                    {actions}
                </Toolbar>
            </AppBar>
            <Container maxWidth="lg" sx={{ py:3 }}>{children}</Container>
        </Box>
    );
}
