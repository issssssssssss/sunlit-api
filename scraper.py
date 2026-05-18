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

    return texto.strip()


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
# CONVERTIR A FLOAT
# =========================

def limpiar_precio(valor):

    try:

        valor = str(valor)\
            .replace(",", "")\
            .replace("$", "")\
            .strip()

        return float(valor)

    except:
        return 0


# =========================
# SCRAPER
# =========================

def obtener_precios():

    options = Options()

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

    cultivos_dict = {}

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

            mercados = []

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

                if len(datos_fila) < 6:
                    continue

                try:

                    valor_dest = datos_fila[2]

                    separado = valor_dest.split(":")

                    if len(separado) >= 2:

                        estado_destino = \
                            separado[0].strip()

                        lugar_destino = \
                            ":".join(
                                separado[1:]
                            ).strip()

                    else:

                        estado_destino = valor_dest

                        lugar_destino = "N/A"

                    mercado = {

                        "fecha":
                            datetime.now()
                            .strftime("%d/%m/%Y"),

                        "producto":
                            producto['nombre'],

                        "presentacion":
                            datos_fila[0],

                        "origen":
                            datos_fila[1],

                        "estado_destino":
                            estado_destino,

                        "lugar_destino":
                            lugar_destino,

                        "precio_min":
                            limpiar_precio(
                                datos_fila[3]
                            ),

                        "precio_max":
                            limpiar_precio(
                                datos_fila[4]
                            ),

                        "precio_frecuente":
                            limpiar_precio(
                                datos_fila[5]
                            ),

                        "observaciones":
                            datos_fila[6]
                            if len(datos_fila) > 6
                            else ""

                    }

                    mercados.append(
                        mercado
                    )

                except Exception as e:

                    print(
                        "ERROR FILA:",
                        e
                    )

            # =========================
            # ESTADISTICAS
            # =========================

            precios = [

                m["precio_frecuente"]

                for m in mercados

                if m["precio_frecuente"] > 0

            ]

            promedio = round(

                sum(precios) / len(precios),

                2

            ) if precios else 0

            cultivos_dict[cultivo_base] = {

                "cultivo":
                    cultivo_base,

                "ultima_actualizacion":
                    datetime.now().strftime(
                        "%d/%m/%Y %H:%M"
                    ),

                "precio_promedio":
                    promedio,

                "total_mercados":
                    len(mercados),

                "total_estados":
                    len(

                        set(
                            m["estado_destino"]
                            for m in mercados
                        )

                    ),

                "total_presentaciones":
                    len(

                        set(
                            m["presentacion"]
                            for m in mercados
                        )

                    ),

                "mercados":
                    mercados

            }

            driver.switch_to.default_content()

        except Exception as e:

            print(
                f"ERROR EN {producto['nombre']}:",
                e
            )

            driver.switch_to.default_content()

    driver.quit()

    resultado_final = {

        "ultima_actualizacion":
            datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            ),

        "cultivos":
            list(
                cultivos_dict.values()
            )

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
        "JSON generado correctamente"
    )

    return resultado_final


# =========================
# EJECUTAR
# =========================

if __name__ == "__main__":

    obtener_precios()