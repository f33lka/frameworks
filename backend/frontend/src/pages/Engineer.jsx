import { useEffect, useState } from 'react';
import api from '../api';
import DefectTable from '../components/DefectTable';

export default function Engineer() {
  const [rows, setRows] = useState([]);

  const fetchMy = async () => {
    const { data } = await api.get('/defects?filter=created_by_me');
    setRows(data);
  };

  useEffect(() => { fetchMy(); }, []);

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Мои дефекты</h1>
        <button className="btn btn-primary">+ Добавить дефект</button>
      </div>
      <DefectTable rows={rows} />
    </div>
  );
}