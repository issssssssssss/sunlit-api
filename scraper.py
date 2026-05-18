import json
import time
import unicodedata
import os

from datetime import datetime

from selenium import webdriver

from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.service import Service

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager


# =========================
# RUTA JSON
# =========================

RUTA_JSON = "data/productos.json"

# =========================
# CREAR CARPETA DATA
# =========================

os.makedirs(
    "data",
    exist_ok=True
)

# =========================
# LIMPIAR TEXTO
# =========================

def limpiar_nombre_producto(texto):

    if not texto:
        return texto

    texto = unicodedata.normalize(
        'NFD',
        texto
    )

    texto = ''.join(

        c for c in texto

        if unicodedata.category(c)
        != 'Mn'

    )

    return texto


# =========================
# CULTIVO BASE
# =========================

def obtener_cultivo_base(nombre_producto):

    nombre_lower = str(
        nombre_producto
    ).lower()

    if 'jitomate' in nombre_lower:
        return 'Tomate'

    if 'tomate' in nombre_lower:
        return 'Tomate'

    if 'papa' in nombre_lower:
        return 'Papa'

    if 'zanahoria' in nombre_lower:
        return 'Zanahoria'

    if 'lechuga' in nombre_lower:
        return 'Lechuga'

    if 'maiz' in nombre_lower:
        return 'Maiz'

    if 'aguacate' in nombre_lower:
        return 'Aguacate'

    if 'cebolla' in nombre_lower:
        return 'Cebolla'

    if 'chile' in nombre_lower:
        return 'Chile'

    return nombre_producto.split(' ')[0]


# =========================
# SCRAPER
# =========================

def obtener_precios():

    options = Options()

    # IMPORTANTE PARA RENDER
    options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")

    options.add_argument(
        "--disable-dev-shm-usage"
    )

    options.add_argument(
        "--disable-gpu"
    )

    options.add_argument(
        "--window-size=1920,1080"
    )

    driver = webdriver.Chrome(

        service=Service(
            ChromeDriverManager().install()
        ),

        options=options

    )

    wait = WebDriverWait(driver, 20)

    # =========================
    # ENTRAR AL MENÚ
    # =========================

    driver.get(
        "https://www.economia-sniim.gob.mx/e_mennal.asp"
    )

    time.sleep(5)

    productos_a_procesar = []

    enlaces = driver.find_elements(
        By.PARTIAL_LINK_TEXT,
        "Precio de"
    )

    print(
        f"Links encontrados: {len(enlaces)}"
    )

    for e in enlaces:

        nombre_crudo = (
            e.text.strip()
            .replace("Precio de ", "")
        )

        nombre_limpio = \
            limpiar_nombre_producto(
                nombre_crudo
            )

        url = e.get_attribute("href")

        productos_a_procesar.append({

            "nombre":
                nombre_limpio,

            "url":
                url

        })

    datos_totales = []

    cultivos_permitidos = [

        "Tomate",
        "Papa",
        "Maiz",
        "Lechuga",
        "Zanahoria",
        "Chile",
        "Cebolla",
        "Aguacate"

    ]

    # =========================
    # RECORRER PRODUCTOS
    # =========================

    for producto in productos_a_procesar:

        cultivo_base = \
            obtener_cultivo_base(
                producto['nombre']
            )

        if cultivo_base not in cultivos_permitidos:
            continue

        print(
            f"Procesando: {producto['nombre']}"
        )

        try:

            driver.get(producto['url'])

            wait.until(

                EC.frame_to_be_available_and_switch_to_it(
                    (By.ID, "ifraHome")
                )

            )

            wait.until(

                EC.presence_of_element_located(
                    (By.ID, "tblResultados")
                )

            )

            tabla = driver.find_element(
                By.ID,
                "tblResultados"
            )

            filas = tabla.find_elements(
                By.TAG_NAME,
                "tr"
            )

            for fila in filas:

                texto_unido = fila.text.strip()

                if (
                    "Presentación"
                    in texto_unido
                ):
                    continue

                if (
                    "NO HAY REGISTROS"
                    in texto_unido
                ):
                    continue

                celdas = fila.find_elements(
                    By.TAG_NAME,
                    "td"
                )

                datos_fila = [

                    c.text.strip()

                    for c in celdas

                ]

                if len(datos_fila) < 7:
                    continue

                try:

                    valor_dest = datos_fila[2]

                    separado = valor_dest.split(":")

                    if len(separado) == 2:

                        estado_destino = \
                            separado[0].strip()

                        lugar_destino = \
                            separado[1].strip()

                    else:

                        estado_destino = \
                            valor_dest

                        lugar_destino = "N/A"

                    documento = {

                        "fecha":
                            datetime.now()
                            .strftime(
                                "%d/%m/%Y"
                            ),

                        "producto":
                            producto['nombre'],

                        "cultivo_base":
                            cultivo_base,

                        "presentacion":
                            datos_fila[0],

                        "origen":
                            datos_fila[1],

                        "estado_destino":
                            estado_destino,

                        "lugar_destino":
                            lugar_destino,

                        "precio_min":
                            datos_fila[4],

                        "precio_max":
                            datos_fila[5],

                        "precio_frecuente":
                            datos_fila[6],

                    }

                    datos_totales.append(
                        documento
                    )

                except Exception as e:

                    print(
                        "ERROR FILA:",
                        e
                    )

            driver.switch_to.default_content()

        except Exception as e:

            print(
                f"ERROR EN {producto['nombre']}:",
                e
            )

            driver.switch_to.default_content()

    # =========================
    # GUARDAR JSON
    # =========================

    resultado_final = {

        "ultima_actualizacion":

            datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            ),

        "productos":
            datos_totales
    }

    with open(

        RUTA_JSON,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            resultado_final,

            f,

            ensure_ascii=False,

            indent=4

        )

    print(
        f"Productos guardados: {len(datos_totales)}"
    )

    driver.quit()

    return datos_totales


# =========================
# EJECUTAR
# =========================

if __name__ == "__main__":

    obtener_precios()