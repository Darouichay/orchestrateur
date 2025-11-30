import libvirt
import os
import subprocess
import xml.etree.ElementTree as ET
import time


class LibvirtService:
    def __init__(self, uri="qemu:///system"):
        self.uri = uri

    def connect(self):
        try:
            return libvirt.open(self.uri)
        except libvirt.libvirtError:
            return None

    def list_vms(self):
        conn = self.connect()
        if not conn:
            return {"error": "Impossible de se connecter à l'hyperviseur"}
        domains = conn.listAllDomains()
        vms = []
        for d in domains:
            info = d.info()
            vms.append({
                "name": d.name(),
                "state": d.state()[0],
                "memory": info[1] // 1024,  # Mo
                "vcpus": info[3],
            })
        conn.close()
        return vms

    def create_vm(self, name, memory=512, disk_size=10, iso_path=None):
        conn = self.connect()
        if not conn:
            return {"error": "Connexion échouée à libvirt (uri: %s)" % self.uri}

        # Chemin du disque
        disk_path = f"/var/lib/libvirt/images/{name}.qcow2"

        # Création du disque qcow2
        try:
            os.system(f"qemu-img create -f qcow2 {disk_path} {disk_size}G")
        except Exception as e:
            return {"error": f"Erreur lors de la création du disque: {e}"}

        # Si une ISO est fournie, on ajoute le lecteur CD
        iso_xml = f"""
            <disk type='file' device='cdrom'>
              <driver name='qemu' type='raw'/>
              <source file='{iso_path}'/>
              <target dev='hda' bus='ide'/>
              <readonly/>
            </disk>
        """ if iso_path else ""

        # XML de la VM
        xml = f"""
            <domain type='kvm'>
              <name>{name}</name>
              <memory unit='MiB'>{memory}</memory>
              <vcpu>1</vcpu>
              <os>
                <type arch='x86_64'>hvm</type>
                <boot dev='cdrom'/>
                <boot dev='hd'/>
              </os>
              <devices>
                <disk type='file' device='disk'>
                  <driver name='qemu' type='qcow2'/>
                  <source file='{disk_path}'/>
                  <target dev='vda' bus='virtio'/>
                </disk>
                {iso_xml}
                <interface type='network'>
                  <source network='default'/>
                  <model type='virtio'/>
                </interface>
                <graphics type='vnc' port='-1'/>
              </devices>
            </domain>
        """

        try:
            dom = conn.defineXML(xml)
            if dom is None:
                conn.close()
                return {"error": "defineXML a renvoyé None (XML invalide ?)"}

            dom.create()
            conn.close()
            return {"message": f"VM '{name}' créée avec succès"}
        except libvirt.libvirtError as e:
            conn.close()
            return {"error": f"Erreur libvirt lors de la création: {e}"}

    def migrate_vm(self, name, destination_uri):
        """
        Migration live d'une VM vers un autre hyperviseur.
        destination_uri doit être de la forme : qemu+ssh://user@IP/system
        """
        if not destination_uri.startswith("qemu+ssh://"):
            return {"error": "URI de destination invalide (attendu: qemu+ssh://user@hote/system)"}

        conn = self.connect()
        if not conn:
            return {"error": "Impossible de se connecter à l'hyperviseur source"}

        try:
            dom = conn.lookupByName(name)
        except libvirt.libvirtError:
            conn.close()
            return {"error": f"VM {name} introuvable sur l'hyperviseur source"}

        # Pour une migration live, la VM doit être active
        if not dom.isActive():
            conn.close()
            return {"error": f"La VM {name} n'est pas active. Démarre-la avant une migration live."}

        cmd = [
            "virsh", "-c", "qemu:///system", "migrate",
            "--live", "--persistent", "--verbose",
            "--copy-storage-all", "--undefinesource",
            name,
            destination_uri,
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            conn.close()
            return {"message": f"Migration de {name} vers {destination_uri} réussie"}
        except subprocess.CalledProcessError as e:
            conn.close()
            return {"error": e.stderr or f"Erreur lors de la migration de {name}"}

    def start_vm(self, name):
        conn = libvirt.open("qemu:///system")
        if not conn:
            return {"error": "Impossible de se connecter à l'hyperviseur"}

        try:
            dom = conn.lookupByName(name)
        except libvirt.libvirtError:
            conn.close()
            return {"error": f"VM {name} introuvable"}

        if dom.isActive():
            conn.close()
            return {"message": f"VM {name} est déjà en cours d'exécution"}

        try:
            dom.create()
            message = f"VM {name} démarrée avec succès"
        except libvirt.libvirtError as e:
            message = f"Erreur lors du démarrage de {name}: {str(e)}"

        conn.close()
        return {"message": message}

    def stop_vm(self, name):
        import time

        conn = libvirt.open("qemu:///system")
        if not conn:
            return {"error": "Impossible de se connecter à l'hyperviseur"}

        try:
            dom = conn.lookupByName(name)
        except libvirt.libvirtError:
            conn.close()
            return {"error": f"VM {name} introuvable"}

        if not dom.isActive():
            conn.close()
            return {"message": f"VM {name} est déjà arrêtée"}

        try:
            dom.shutdown()
            for _ in range(5):
                time.sleep(1)
                if not dom.isActive():
                    break
            if dom.isActive():
                dom.destroy()
            message = f"VM {name} arrêtée avec succès"
        except libvirt.libvirtError as e:
            message = f"Erreur lors de l'arrêt de {name}: {str(e)}"

        conn.close()
        return {"message": message}
    def reboot_vm(self, name):
        """
        Redémarrage "hard" d'une VM :
        - si la VM est active : destroy -> attendre qu'elle soit éteinte -> pause 2s -> start
        - si la VM est arrêtée : start
        """
        conn = self.connect()
        if not conn:
            return {"error": "Impossible de se connecter à l'hyperviseur"}

        try:
            dom = conn.lookupByName(name)
        except libvirt.libvirtError:
            conn.close()
            return {"error": f"VM {name} introuvable"}

        try:
            if dom.isActive():
                # On arrête brutalement
                dom.destroy()

                # On attend qu'elle soit vraiment éteinte (max ~2s)
                for _ in range(10):
                    time.sleep(0.2)
                    if not dom.isActive():
                        break

                # On laisse 2 secondes bien visibles en "éteinte"
                time.sleep(2)

                # On redémarre
                dom.create()
                message = f"VM {name} redémarrée (destroy + pause + start)"
            else:
                # Si elle est déjà éteinte, on la démarre simplement
                dom.create()
                message = f"VM {name} était arrêtée, elle a été démarrée."
        except libvirt.libvirtError as e:
            conn.close()
            return {"error": f"Erreur libvirt lors du redémarrage de {name}: {str(e)}"}
        except Exception as e:
            # Pour éviter les 500 si autre chose casse (ex: NameError, etc.)
            conn.close()
            return {"error": f"Erreur inattendue lors du redémarrage de {name}: {str(e)}"}

        conn.close()
        return {"message": message}





    def suspend_vm(self, name):
        conn = self.connect()
        if not conn:
            return {"error": "Connexion échouée"}
        try:
            dom = conn.lookupByName(name)
        except libvirt.libvirtError:
            conn.close()
            return {"error": f"VM {name} introuvable"}

        if not dom.isActive():
            conn.close()
            return {"message": f"VM {name} est déjà arrêtée"}

        try:
            # Si la VM est en pause, on reprend
            if dom.info()[0] == libvirt.VIR_DOMAIN_PAUSED:
                dom.resume()
                message = f"VM {name} reprise avec succès"
            else:
                dom.suspend()
                message = f"VM {name} suspendue avec succès"
        except libvirt.libvirtError as e:
            message = f"Erreur lors de la suspension/reprise de {name}: {str(e)}"

        conn.close()
        return {"message": message}

    def get_console_uri(self, name: str):
        """
        Retourne l'URI VNC de la VM sous la forme vnc://host:port
        (nécessite que la VM soit démarrée et ait un graphics type='vnc')
        """
        conn = self.connect()
        if not conn:
            return {"error": "Impossible de se connecter à l'hyperviseur"}

        try:
            dom = conn.lookupByName(name)
        except libvirt.libvirtError:
            conn.close()
            return {"error": f"VM {name} introuvable"}

        try:
            xml_desc = dom.XMLDesc()
        except libvirt.libvirtError as e:
            conn.close()
            return {"error": f"Impossible de récupérer le XML de {name} : {e}"}

        try:
            root = ET.fromstring(xml_desc)
            gfx = root.find("./devices/graphics[@type='vnc']")
            if gfx is None:
                conn.close()
                return {"error": "Aucune console VNC définie pour cette VM"}

            port = gfx.get("port")
            listen = gfx.get("listen") or "127.0.0.1"

            if port is None or port == "-1":
                conn.close()
                return {"error": "Port VNC non encore assigné. Vérifie que la VM est démarrée."}

            uri = f"vnc://{listen}:{port}"
            conn.close()
            return {"uri": uri}
        except Exception as e:
            conn.close()
            return {"error": f"Erreur lors de l'analyse du XML de {name} : {e}"}

    def clone_vm(self, source_name, target_name):
        """
        Clone une VM :
        - copie du disque qcow2
        - copie du XML libvirt
        - création d'une nouvelle VM avec un nom différent
        """
        conn = self.connect()
        if not conn:
            return {"error": "Impossible de se connecter à l'hyperviseur"}

        # 1. Récupérer la VM source
        try:
            dom_src = conn.lookupByName(source_name)
        except libvirt.libvirtError:
            conn.close()
            return {"error": f"VM source {source_name} introuvable"}

        # 2. Récupérer le XML source
        xml_src = dom_src.XMLDesc()

        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_src)

        # Changer le nom
        name_elem = root.find("name")
        name_elem.text = target_name

        # Supprimer l'UUID pour en générer un nouveau
        uuid_elem = root.find("uuid")
        if uuid_elem is not None:
            root.remove(uuid_elem)

        # 3. Récupérer le disque de la VM source
        disk_path_src = None
        for disk in root.findall("./devices/disk"):
            if disk.get("device") == "disk":
                source = disk.find("source")
                if source is not None and "file" in source.attrib:
                    disk_path_src = source.attrib["file"]
                    break

        if not disk_path_src:
            conn.close()
            return {"error": "Impossible de trouver le disque source"}

        # Nouveau disque
        disk_path_dst = f"/var/lib/libvirt/images/{target_name}.qcow2"

        # Copier le disque
        os.system(f"cp {disk_path_src} {disk_path_dst}")

        # Modifier le XML avec le nouveau chemin
        for disk in root.findall("./devices/disk"):
            if disk.get("device") == "disk":
                source = disk.find("source")
                source.set("file", disk_path_dst)

        # 4. Générer le nouveau XML
        new_xml = ET.tostring(root, encoding="unicode")

        # 5. Définir la nouvelle VM
        try:
            dom_new = conn.defineXML(new_xml)
            if dom_new is None:
                conn.close()
                return {"error": "Impossible de définir la VM clonée"}
        except libvirt.libvirtError as e:
            conn.close()
            return {"error": f"Erreur libvirt : {e}"}

        conn.close()
        return {"message": f"VM {source_name} clonée vers {target_name}"}



    def delete_vm(self, name):
        """
        Supprime une VM proprement :
        - supprime tous les snapshots (obligatoire sinon libvirt bloque)
        - stoppe si active
        - undefine avec les bons flags
        - supprime le disque qcow2
        """
        conn = self.connect()
        if not conn:
            return {"error": "Impossible de se connecter à l'hyperviseur"}

        # Récupération du domaine
        try:
            dom = conn.lookupByName(name)
        except libvirt.libvirtError:
            conn.close()
            return {"error": f"VM {name} introuvable"}

        # 🔥 1) SI ACTIVE → STOP FORCE
        try:
            if dom.isActive():
                dom.destroy()   # arrêt immédiat (obligatoire avant suppression)
        except libvirt.libvirtError as e:
            conn.close()
            return {"error": f"Impossible d'arrêter la VM {name} : {e}"}

        # 🔥 2) SUPPRIMER AUTOMATIQUEMENT LES SNAPSHOTS
        try:
            snapshots = dom.snapshotListNames()
            for snap_name in snapshots:
                snap = dom.snapshotLookupByName(snap_name)
                snap.delete()   # suppression individuelle
        except libvirt.libvirtError:
            pass  # s'il n'y a pas de snapshots → ok

        # 🔥 3) Récupérer le disque principal via le XML
        try:
            xml_desc = dom.XMLDesc()
        except libvirt.libvirtError as e:
            conn.close()
            return {"error": f"Impossible de récupérer le XML de {name} : {e}"}

        import xml.etree.ElementTree as ET
        disk_path = None
        try:
            root = ET.fromstring(xml_desc)
            for disk in root.findall("./devices/disk"):
                if disk.get("device") == "disk":
                    source = disk.find("source")
                    if source is not None:
                        disk_path = source.attrib.get("file")
                    break
        except Exception:
            disk_path = None

        # 🔥 4) UNDEFINE AVEC FLAGS SNAPSHOT
        try:
            if hasattr(libvirt, "VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA"):
                dom.undefineFlags(
                    libvirt.VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA |
                    libvirt.VIR_DOMAIN_UNDEFINE_MANAGED_SAVE
                )
            else:
                dom.undefine()
        except libvirt.libvirtError as e:
            conn.close()
            return {"error": f"Impossible de supprimer la définition de {name} : {e}"}

        conn.close()

        # 🔥 5) SUPPRIMER LE DISQUE QCOW2
        if disk_path and os.path.exists(disk_path):
            try:
                os.remove(disk_path)
            except OSError as e:
                return {
                    "message": f"VM {name} supprimée mais disque NON supprimé ({e.strerror})",
                    "disk_path": disk_path,
                }

        return {"message": f"VM {name} et son disque ont été supprimés avec succès"}



    def snapshot_create(self, name, snapshot_name):
        conn = self.connect()
        if not conn:
            return {"error": "Connexion à libvirt impossible"}

        try:
            dom = conn.lookupByName(name)
        except libvirt.libvirtError:
            conn.close()
            return {"error": f"VM {name} introuvable"}

        is_running = dom.isActive()

        # VM en marche → snapshot AVEC mémoire (live)
        if is_running:
            xml = f"""
            <domainsnapshot>
                <name>{snapshot_name}</name>
                <description>Live snapshot créé par orchestrateur</description>
                <memory snapshot='internal'/>
                <disks>
                    <disk name='vda' snapshot='internal'/>
                </disks>
            </domainsnapshot>
            """
        else:
            # VM arrêtée → snapshot SANS mémoire
            xml = f"""
            <domainsnapshot>
                <name>{snapshot_name}</name>
                <description>Snapshot (offline) créé par orchestrateur</description>
                <memory snapshot='no'/>
                <disks>
                    <disk name='vda' snapshot='internal'/>
                </disks>
            </domainsnapshot>
            """

        try:
            dom.snapshotCreateXML(xml, 0)
            conn.close()
            return {"message": f"Snapshot '{snapshot_name}' créé avec succès"}
        except libvirt.libvirtError as e:
            conn.close()
            return {"error": str(e)}


    def snapshot_list(self, name):
        conn = self.connect()
        if not conn:
            return {"error": "Connexion impossible"}

        try:
            dom = conn.lookupByName(name)
            snaps = dom.snapshotListNames()
            conn.close()
            return {"snapshots": snaps}
        except libvirt.libvirtError as e:
            conn.close()
            return {"error": str(e)}

    def snapshot_restore(self, name, snapshot_name):
        conn = self.connect()
        if not conn:
            return {"error": "Connexion impossible"}

        try:
            dom = conn.lookupByName(name)
            snapshot = dom.snapshotLookupByName(snapshot_name, 0)
            dom.revertToSnapshot(snapshot, 0)
            conn.close()
            return {"message": f"Snapshot '{snapshot_name}' restauré"}
        except libvirt.libvirtError as e:
            conn.close()
            return {"error": str(e)}


    def snapshot_delete(self, name, snapshot_name):
        conn = self.connect()
        if not conn:
            return {"error": "Connexion impossible"}

        try:
            dom = conn.lookupByName(name)
            snapshot = dom.snapshotLookupByName(snapshot_name, 0)
            snapshot.delete(flags=0)
            conn.close()
            return {"message": f"Snapshot '{snapshot_name}' supprimé"}
        except libvirt.libvirtError as e:
            conn.close()
            return {"error": str(e)}

