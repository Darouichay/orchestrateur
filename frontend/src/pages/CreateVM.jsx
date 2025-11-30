import { useState } from "react";
import api from "../services/api";

function CreateVM({ onCreated }) {
  const [name, setName] = useState("");
  const [diskSize, setDiskSize] = useState(10);
  const [memory, setMemory] = useState(512); // le backend met 512 par défaut si non fourni
  const [isoFile, setIsoFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    if (!name) {
      return alert("Nom de la VM requis");
    }
    if (!isoFile) {
      return alert("ISO requis pour créer la VM");
    }
    if (diskSize < 5) {
      const confirmSmallDisk = window.confirm(
        "Moins de 5 Go, c'est très peu pour un OS. Continuer quand même ?"
      );
      if (!confirmSmallDisk) return;
    }

    const formData = new FormData();
    formData.append("name", name);
    formData.append("disk_size", diskSize);
    formData.append("iso", isoFile);
    // memory est optionnel, mais on l'envoie quand même
    if (memory) {
      formData.append("memory", memory);
    }

    try {
      setLoading(true);
      const res = await api.post("/vms/create", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const msg =
        res?.data?.message ||
        "VM créée. Vérifie dans 'virsh list --all' si tout est OK.";
      alert(msg);

      // reset du formulaire
      setName("");
      setDiskSize(10);
      setMemory(512);
      setIsoFile(null);

      if (onCreated) {
        onCreated(); // rafraîchit la liste dans le Dashboard
      }
    } catch (err) {
      const errMsg =
        err?.response?.data?.error || err.message || String(err);
      alert("Erreur lors de la création de la VM : " + errMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mb-6 border rounded p-4">
      <h2 className="text-xl font-semibold mb-2">Créer une VM</h2>

      <div className="mb-2">
        <label className="block text-sm mb-1">Nom de la VM</label>
        <input
          type="text"
          placeholder="debian-vm"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="border p-2 rounded w-full"
        />
      </div>

      <div className="mb-2">
        <label className="block text-sm mb-1">Taille du disque (Go)</label>
        <input
          type="number"
          placeholder="Disque (Go)"
          value={diskSize}
          min={2}
          onChange={(e) => setDiskSize(Number(e.target.value))}
          className="border p-2 rounded w-32"
        />
      </div>

      <div className="mb-2">
        <label className="block text-sm mb-1">Mémoire (Mo)</label>
        <input
          type="number"
          placeholder="512"
          value={memory}
          min={256}
          onChange={(e) => setMemory(Number(e.target.value))}
          className="border p-2 rounded w-32"
        />
        <p className="text-xs text-gray-500">
          Si tu laisses 512, ça crée une VM avec 512 Mo de RAM.
        </p>
      </div>

      <div className="mb-2">
        <label className="block text-sm mb-1">Fichier ISO</label>
        <input
          type="file"
          accept=".iso"
          onChange={(e) => setIsoFile(e.target.files[0])}
          className="border p-2 rounded w-full"
        />
      </div>

      <button
        onClick={handleCreate}
        disabled={loading}
        className="bg-green-500 text-white px-4 py-2 rounded mt-2 disabled:opacity-60"
      >
        {loading ? "Création en cours..." : "Créer"}
      </button>
    </div>
  );
}

export default CreateVM;
