import { useEffect, useState } from 'react';
import api from '../api';
import DefectTable from '../components/DefectTable';
import ExportButton from '../components/ExportButton';

export default function Manager() {
  const [rows, setRows] = useState([]);

  const fetchAll = async () => {
    const { data } = await api.get('/defects');
    setRows(data);
  };

  useEffect(() => { fetchAll(); }, []);

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Управление дефектами</h1>
        <div className="flex gap-2">
          <ExportButton />
        </div>
      </div>
      <DefectTable rows={rows} />
    </div>
  );
}