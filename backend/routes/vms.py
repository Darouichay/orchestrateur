from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import JSONResponse
from services.libvirt_service import LibvirtService
import os

router = APIRouter()
service = LibvirtService()

# Dossier où enregistrer les ISO
UPLOAD_DIR = "/var/lib/libvirt/iso_uploads"


@router.get("/")
def list_vms():
    return service.list_vms()


@router.post("/create")
async def create_vm(
    name: str = Form(...),
    memory: int = Form(None),
    disk_size: int = Form(10),
    iso: UploadFile = File(None)
):
    memory = memory or 512

    iso_path = None
    if iso:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        iso_path = os.path.join(UPLOAD_DIR, iso.filename)
        try:
            with open(iso_path, "wb") as f:
                f.write(await iso.read())
        except OSError as e:
            raise HTTPException(
                status_code=507,
                detail=f"Impossible d'écrire l'ISO ({e.strerror}). Vérifie l'espace disque."
            )

    result = service.create_vm(
        name=name,
        memory=memory,
        disk_size=disk_size,
        iso_path=iso_path
    )

    if "error" in result:
        return JSONResponse(status_code=400, content={"error": result["error"]})

    return result


@router.delete("/delete/{name}")
def delete_vm(name: str):
    result = service.delete_vm(name)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/migrate/{name}")
def migrate_vm(name: str, destination: str = Query(...)):
    """
    Migration d'une VM vers un autre hyperviseur.
    destination = qemu+ssh://user@IP/system
    """
    result = service.migrate_vm(name, destination)

    # 🔥 TRÈS IMPORTANT : renvoyer { "error": "..." }
    # pour que le frontend puisse l'afficher dans alert()
    if "error" in result:
        return JSONResponse(status_code=400, content={"error": result["error"]})

    return result


@router.post("/{name}/start")
def start_vm(name: str):
    return service.start_vm(name)


@router.post("/{name}/stop")
def stop_vm(name: str):
    return service.stop_vm(name)


@router.post("/{name}/suspend")
def suspend_vm(name: str):
    return service.suspend_vm(name)


@router.post("/{name}/reboot")
def reboot_vm(name: str):
    result = service.reboot_vm(name)
    if "error" in result:
        return JSONResponse(status_code=400, content={"error": result["error"]})
    return result

@router.get("/{name}/console")
def get_vm_console(name: str):
    """
    Retourne l'URI VNC de la VM pour ouvrir une console (ex: vnc://127.0.0.1:5901)
    """
    result = service.get_console_uri(name)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/clone")
def clone_vm(source: str = Form(...), target: str = Form(...)):
    result = service.clone_vm(source, target)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{name}/snapshot/create")
def create_snapshot(name: str, snapshot_name: str = Form(...)):
    return service.snapshot_create(name, snapshot_name)

@router.get("/{name}/snapshot/list")
def list_snapshots(name: str):
    return service.snapshot_list(name)

@router.post("/{name}/snapshot/restore")
def restore_snapshot(name: str, snapshot_name: str = Form(...)):
    return service.snapshot_restore(name, snapshot_name)

@router.post("/{name}/snapshot/delete")
def delete_snapshot(name: str, snapshot_name: str = Form(...)):
    return service.snapshot_delete(name, snapshot_name)
