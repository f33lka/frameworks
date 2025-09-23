export default function DefectTable({ rows = [] }) {
  return (
    <div className="overflow-x-auto">
      <table className="table table-compact w-full">
        <thead>
          <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Статус</th>
            <th>Приоритет</th>
            <th>Исполнитель</th>
            <th>Срок</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((d) => (
            <tr key={d.id}>
              <th>{d.id}</th>
              <td>{d.title}</td>
              <td>{d.status}</td>
              <td>{d.priority}</td>
              <td>{d.assignee?.full_name || '-'}</td>
              <td>{d.due_date ? new Date(d.due_date).toLocaleDateString('ru') : '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}