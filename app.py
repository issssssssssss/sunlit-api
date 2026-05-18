from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# RUTA JSON
# =========================

RUTA_JSON = "data/productos.json"

# =========================
# LEER JSON
# =========================

def leer_json():

    if not os.path.exists(RUTA_JSON):
        return {
            "ultima_actualizacion": None,
            "productos": []
        }

    with open(
        RUTA_JSON,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

# =========================
# HOME
# =========================

@app.get("/")
def home():

    return {
        "mensaje": "SunLit API funcionando"
    }

# =========================
# TODOS LOS PRODUCTOS
# =========================

@app.get("/productos")
def productos():

    return leer_json()

# =========================
# FILTRAR POR CULTIVO
# =========================

@app.get("/producto/{nombre}")
def producto(nombre: str):

    datos = leer_json()

    productos = datos.get(
        "productos",
        []
    )

    filtrados = [

        item for item in productos

        if nombre.lower()
        in item["cultivo_base"].lower()

    ]

    return {
        "ultima_actualizacion":
            datos.get(
                "ultima_actualizacion"
            ),

        "productos":
            filtrados
    }