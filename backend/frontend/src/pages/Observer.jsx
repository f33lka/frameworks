import { useEffect, useState } from 'react';
import api from '../api';
import DefectTable from '../components/DefectTable';

export default function Observer() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    api.get('/defects').then((r) => setRows(r.data));
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Обзор дефектов</h1>
      <DefectTable rows={rows} />
    </div>
  );
}