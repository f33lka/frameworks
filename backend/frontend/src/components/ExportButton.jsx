import api from '../api';

export default function ExportButton() {
  const load = async () => {
    const res = await api.get('/reports/export?format=xlsx', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const a = document.createElement('a');
    a.href = url;
    a.download = 'defects.xlsx';
    a.click();
  };

  return (
    <button onClick={load} className="btn btn-outline">
      Экспорт Excel
    </button>
  );
}