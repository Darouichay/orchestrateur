from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ✅ ajout ici
from routes import vms, hypervisors

app = FastAPI(title="Mini Orchestrateur Hyperviseurs")

# ✅ Ajout du middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tu peux mettre ["http://localhost:3000"] pour restreindre
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Inclusion des routes
app.include_router(vms.router, prefix="/vms", tags=["VMs"])
app.include_router(hypervisors.router, prefix="/hypervisors", tags=["Hyperviseurs"])

@app.get("/")
def root():
    return {"message": "Orchestrateur d'hyperviseurs en ligne"}

