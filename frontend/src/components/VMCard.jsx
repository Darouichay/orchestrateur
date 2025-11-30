import {
  Play,
  Square,
  Pause,
  RefreshCw,
  Terminal,
  Copy,
  Trash2,
  Camera,
  List,
  RotateCcw,
  MoveRight
} from "lucide-react";

const VMCard = ({
  vm,
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
  onSnapshotDelete,
}) => {

  const getStateLabel = (state) => {
    switch (state) {
      case 1: return "Running";
      case 3: return "Paused";
      case 5: return "Shutoff";
      default: return "Unknown";
    }
  };

  const stateColor = (state) => {
    switch (state) {
      case 1: return "text-green-600 bg-green-100";
      case 3: return "text-yellow-600 bg-yellow-100";
      case 5: return "text-red-600 bg-red-100";
      default: return "text-gray-600 bg-gray-100";
    }
  };

  return (
    <div className="border rounded-xl p-5 shadow-md hover:shadow-lg transition bg-white">
      <div className="flex justify-between items-center">
        <h2 className="font-semibold text-lg">{vm.name}</h2>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${stateColor(vm.state)}`}>
          {getStateLabel(vm.state)}
        </span>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2 text-sm">

        <button onClick={() => onStart(vm.name)} className="action-btn bg-green-500">
          <Play size={16} /> Start
        </button>
        <button onClick={() => onStop(vm.name)} className="action-btn bg-red-500">
          <Square size={16} /> Stop
        </button>
        <button onClick={() => onSuspend(vm.name)} className="action-btn bg-yellow-500">
          <Pause size={16} /> Pause
        </button>
        <button onClick={() => onReboot(vm.name)} className="action-btn bg-blue-600">
          <RefreshCw size={16} /> Reboot
        </button>

        <button onClick={() => onConsole(vm.name)} className="action-btn bg-indigo-600">
          <Terminal size={16} /> Console
        </button>
        <button onClick={() => onClone(vm.name)} className="action-btn bg-purple-600">
          <Copy size={16} /> Clone
        </button>
        <button onClick={() => onMigrate(vm.name)} className="action-btn bg-blue-700">
          <MoveRight size={16} /> Migrate
        </button>

        <button onClick={() => onDelete(vm.name)} className="action-btn bg-gray-700">
          <Trash2 size={16} /> Delete
        </button>

        <button onClick={() => onSnapshotCreate(vm.name)} className="action-btn bg-pink-600">
          <Camera size={16} /> Snapshot
        </button>
        <button onClick={() => onSnapshotList(vm.name)} className="action-btn bg-pink-500">
          <List size={16} /> List
        </button>
        <button onClick={() => onSnapshotRestore(vm.name)} className="action-btn bg-pink-500">
          <RotateCcw size={16} /> Restore
        </button>
        <button onClick={() => onSnapshotDelete(vm.name)} className="action-btn bg-pink-700">
          <Trash2 size={16} /> Delete Snap
        </button>

      </div>
    </div>
  );
};

export default VMCard;
