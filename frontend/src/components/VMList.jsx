import VMCard from "./VMCard";

function VMList({
  vms,
  onDelete,
  onMigrate,
  onStart,
  onStop,
  onSuspend,
  onReboot,
  onConsole,
  onClone,
  onSnapshotCreate,
  onSnapshotList,
  onSnapshotRestore,
  onSnapshotDelete
}) {
  return (
    <div className="mt-6">
      <h2 className="text-2xl font-bold mb-4">Machines Virtuelles</h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {vms.map((vm, i) => (
          <VMCard
            key={i}
            vm={vm}
            onDelete={onDelete}
            onMigrate={onMigrate}
            onStart={onStart}
            onStop={onStop}
            onSuspend={onSuspend}
            onReboot={onReboot}
            onConsole={onConsole}
            onClone={onClone}
            onSnapshotCreate={onSnapshotCreate}
            onSnapshotList={onSnapshotList}
            onSnapshotRestore={onSnapshotRestore}
            onSnapshotDelete={onSnapshotDelete}
          />
        ))}
      </div>
    </div>
  );
}

export default VMList;
