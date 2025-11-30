function HypervisorList({ hypervisors }) {
  return (
    <div className="mb-6">
      <h2 className="text-xl font-semibold mb-2">Hyperviseurs</h2>
      <ul>
        {hypervisors.map((h, i) => (
          <li key={i} className="bg-gray-100 p-2 rounded mb-1">{h}</li>
        ))}
      </ul>
    </div>
  );
}

export default HypervisorList;
