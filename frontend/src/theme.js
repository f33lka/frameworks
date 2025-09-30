import { createTheme } from '@mui/material/styles';
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#4f46e5' },
    secondary: { main: '#06b6d4' },
    background: { default: '#f6f7fb' }
  },
  typography: {
    fontFamily: '"Inter","Roboto","Helvetica","Arial",sans-serif',
    h5: { fontWeight: 700 }, h6: { fontWeight: 700 }
  },
  shape: { borderRadius: 12 }
});
export default theme;
