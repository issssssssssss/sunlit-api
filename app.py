from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from unidecode import unidecode

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
            "cultivos": []
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
# TODOS LOS CULTIVOS
# =========================

@app.get("/productos")
def productos():

    return leer_json()

# =========================
# FILTRAR CULTIVO
# =========================

@app.get("/producto/{nombre}")
def producto(nombre: str):

    datos = leer_json()

    cultivos = datos.get(
        "cultivos",
        []
    )

    nombre_normalizado = unidecode(
        nombre.lower()
    )

    cultivo_encontrado = None

    for cultivo in cultivos:

        cultivo_normalizado = unidecode(

            cultivo["cultivo"]
            .lower()

        )

        if (
            nombre_normalizado
            in cultivo_normalizado
        ):

            cultivo_encontrado = cultivo
            break

    # =========================
    # SI NO EXISTE
    # =========================

    if not cultivo_encontrado:

        return {

            "cultivo": nombre,

            "ultima_actualizacion":
                datos.get(
                    "ultima_actualizacion"
                ),

            "precio_promedio": 0,

            "total_mercados": 0,

            "total_estados": 0,

            "total_presentaciones": 0,

            "mercados": []

        }

    # =========================
    # RESPUESTA
    # =========================

    return cultivo_encontrado