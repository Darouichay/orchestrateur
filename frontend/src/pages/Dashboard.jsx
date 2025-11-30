import { useEffect, useState } from "react";
import api from "../services/api";
import VMList from "../components/VMList";
import HypervisorList from "../components/HypervisorList";
import CreateVM from "./CreateVM";

function Dashboard() {
  const [vms, setVms] = useState([]);
  const [hypervisors, setHypervisors] = useState([]);
  const [actionInProgress, setActionInProgress] = useState(false);

  const fetchData = async () => {
    try {
      const vmsRes = await api.get("/vms/");
      const hypervisorsRes = await api.get("/hypervisors/");
      setVms(vmsRes?.data || []);
      setHypervisors(hypervisorsRes?.data?.hypervisors || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (actionInProgress) return; // stop polling during actions

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [actionInProgress]);

  /* ---------------- SNAPSHOT ACTIONS ---------------- */

  const handleSnapshotCreate = async (vmName) => {
    const snap = prompt("Nom du snapshot ?");
    if (!snap) return;

    setActionInProgress(true);
    try {
      const form = new FormData();
      form.append("snapshot_name", snap);

      const res = await api.post(`/vms/${vmName}/snapshot/create`, form);
      alert(res.data.message);
      await fetchData();
    } catch (err) {
      alert(err?.response?.data?.detail || err.message);
    }
    setActionInProgress(false);
  };

  const handleSnapshotList = async (vmName) => {
    setActionInProgress(true);
    try {
      const res = await api.get(`/vms/${vmName}/snapshot/list`);
      alert("Snapshots : " + res.data.snapshots.join(", "));
    } catch (err) {
      alert(err?.response?.data?.detail || err.message);
    }
    setActionInProgress(false);
  };

  const handleSnapshotRestore = async (vmName) => {
    const snap = prompt("Snapshot à restaurer ?");
    if (!snap) return;

    setActionInProgress(true);
    try {
      const form = new FormData();
      form.append("snapshot_name", snap);

      const res = await api.post(`/vms/${vmName}/snapshot/restore`, form);
      alert(res.data.message);
      await fetchData();
    } catch (err) {
      alert(err?.response?.data?.detail || err.message);
    }
    setActionInProgress(false);
  };

  const handleSnapshotDelete = async (vmName) => {
    const snap = prompt("Snapshot à supprimer ?");
    if (!snap) return;

    setActionInProgress(true);
    try {
      const form = new FormData();
      form.append("snapshot_name", snap);

      const res = await api.post(`/vms/${vmName}/snapshot/delete`, form);
      alert(res.data.message);
      await fetchData();
    } catch (err) {
      alert(err?.response?.data?.detail || err.message);
    }
    setActionInProgress(false);
  };

  /* ---------------------- BASIC ACTIONS ---------------------- */

  const handleDelete = async (name) => {
    if (!window.confirm(`Supprimer ${name} ?`)) return;

    setActionInProgress(true);
    try {
      await api.delete(`/vms/delete/${name}`);
      await fetchData();
    } catch (err) {
      alert(err?.response?.data?.error || err.message);
    }
    setActionInProgress(false);
  };

  const handleAction = async (vmName, action) => {
    setActionInProgress(true);
    try {
      const res = await api.post(`/vms/${vmName}/${action}`);
      alert(res.data.message);
      await fetchData();
    } catch (err) {
      alert(err?.response?.data?.error || err.message);
    }
    setActionInProgress(false);
  };

  const handleReboot = (vmName) => handleAction(vmName, "reboot");

  const handleConsole = async (vmName) => {
    setActionInProgress(true);
    try {
      const res = await api.get(`/vms/${vmName}/console`);
      if (!res?.data?.uri) alert("URI console introuvable");
      else window.location.href = res.data.uri;
    } catch (err) {
      alert(err?.response?.data?.detail || err.message);
    }
    setActionInProgress(false);
  };

  /* ---------------------- CLONE ---------------------- */

  const handleClone = async (sourceName) => {
    const target = prompt("Nom de la VM clonée :");
    if (!target) return;

    setActionInProgress(true);
    try {
      const form = new FormData();
      form.append("source", sourceName);
      form.append("target", target);

      const res = await api.post("/vms/clone", form);
      alert(res.data.message);
      await fetchData();
    } catch (err) {
      alert(err?.response?.data?.detail || err.message);
    }
    setActionInProgress(false);
  };

  /* --------------------- MIGRATE --------------------- */

  const handleMigrate = async (name) => {
    const dest = prompt("IP destination ?");
    if (!dest) return;

    setActionInProgress(true);
    try {
      const uri = `qemu+ssh://user@${dest}/system`;
      const res = await api.post(`/vms/migrate/${name}`, null, {
        params: { destination: uri },
      });
      alert(res.data.message);
      await fetchData();
    } catch (err) {
      alert(err?.response?.data?.error || err.message);
    }
    setActionInProgress(false);
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-4">Orchestrateur d'Hyperviseurs</h1>

      <HypervisorList hypervisors={hypervisors} />

      <CreateVM onCreated={fetchData} />

      <VMList
        vms={vms}
        onDelete={handleDelete}
        onStart={(n) => handleAction(n, "start")}
        onStop={(n) => handleAction(n, "stop")}
        onSuspend={(n) => handleAction(n, "suspend")}
        onReboot={handleReboot}
        onConsole={handleConsole}
        onClone={handleClone}
        onSnapshotCreate={handleSnapshotCreate}
        onSnapshotList={handleSnapshotList}
        onSnapshotRestore={handleSnapshotRestore}
        onSnapshotDelete={handleSnapshotDelete}
        onMigrate={handleMigrate}
      />
    </div>
  );
}

export default Dashboard;
