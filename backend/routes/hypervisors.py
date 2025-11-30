from fastapi import APIRouter
from services.libvirt_service import LibvirtService

router = APIRouter()
service = LibvirtService()

@router.get("/")
def list_hypervisors():
    # Ici, on pourrait gérer plusieurs hyperviseurs via une base de données
    return {"hypervisors": [service.uri]}
