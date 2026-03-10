# ================= aemet.py =================
import requests
import time
import pandas as pd
import re
from config import API_KEY

headers = {"api_key": API_KEY, "Accept": "application/json"}

def hacer_peticion_aemet(url, intentos=3, espera=2):
    """Realiza una petición a AEMET con reintentos"""
    for intento in range(intentos):
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                return r
            elif r.status_code == 429:
                print(f"⚠ Límite excedido. Esperando {espera * (intento + 1)}s...")
                time.sleep(espera * (intento + 1))
            else:
                print(f"⚠ Error {r.status_code}. Reintentando...")
                time.sleep(espera)
        except Exception as e:
            print(f"⚠ Error: {e}")
            time.sleep(espera)
    return None

def obtener_prediccion(municipio):
    """Obtiene la predicción de AEMET para un municipio específico"""
    print(f"📡 Obteniendo datos para municipio {municipio}...")
    
    url = f"https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/{municipio}"
    
    r = hacer_peticion_aemet(url)
    if not r:
        print("❌ No se pudo conectar con AEMET")
        return None
        
    respuesta = r.json()
    if "datos" not in respuesta:
        print("❌ Respuesta inesperada de AEMET")
        return None
        
    time.sleep(1)
    r2 = hacer_peticion_aemet(respuesta["datos"])
    if not r2:
        print("❌ No se pudieron descargar los datos")
        return None
        
    return r2.json()[0]["prediccion"]["dia"][:7]

def procesar_datos(dias):
    """Convierte los datos de AEMET a DataFrame"""
    filas = []
    for d in dias:
        # Manejar posibles variaciones en los datos
        estado = d["estadoCielo"][0]["descripcion"] if "estadoCielo" in d else "Despejado"
        codigo = d["estadoCielo"][0]["value"] if "estadoCielo" in d else "11"
        lluvia = int(d["probPrecipitacion"][0]["value"]) if "probPrecipitacion" in d else 0
        viento_dir = d["viento"][0]["direccion"] if "viento" in d else "Variable"
        viento_vel = d["viento"][0]["velocidad"] if "viento" in d else 0
        
        filas.append({
            "fecha": d["fecha"],
            "tmax": int(d["temperatura"]["maxima"]),
            "tmin": int(d["temperatura"]["minima"]),
            "estado": estado,
            "codigo": codigo,
            "lluvia": lluvia,
            "viento": f'{viento_dir} {viento_vel} km/h'
        })
    
    df = pd.DataFrame(filas)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df

def obtener_alertas_oficiales(area):
    """Obtiene alertas oficiales para un área específica"""
    print(f"📡 Obteniendo alertas para área {area}...")
    
    # Algunas áreas pueden no tener alertas (error 404 es normal)
    url_alertas = f"https://opendata.aemet.es/opendata/api/alertas/area/{area}"
    
    try:
        # Primera petición para obtener la URL de datos
        r = hacer_peticion_aemet(url_alertas, intentos=2)  # Reducimos intentos para alertas
        if not r:
            print(f"ℹ No hay alertas disponibles para {area} (servicio no responde)")
            return []
        
        if r.status_code != 200:
            # El error 404 es normal cuando no hay alertas en esa área
            if r.status_code == 404:
                print(f"ℹ No hay alertas activas para {area}")
            else:
                print(f"⚠ Código de error {r.status_code} para {area}")
            return []
        
        respuesta = r.json()
        if "datos" not in respuesta:
            print(f"ℹ Formato de respuesta inesperado para {area}")
            return []
        
        datos_url = respuesta["datos"]
        
        # Pequeña pausa antes de la segunda petición
        time.sleep(1)
        
        # Segunda petición para descargar los datos
        r2 = hacer_peticion_aemet(datos_url, intentos=2)
        if not r2:
            return []
        
        alertas_data = r2.json()
        alertas_procesadas = []
        
        # Procesar alertas
        if isinstance(alertas_data, dict):
            for zona, alertas_zona in alertas_data.items():
                if isinstance(alertas_zona, list):
                    for alerta in alertas_zona:
                        if isinstance(alerta, dict):
                            nivel = alerta.get('nivel', '')
                            fenomeno = alerta.get('fenomeno', '')
                            descripcion = alerta.get('descripcion', '')
                            
                            if nivel == 'rojo':
                                nivel_texto = "🔴 AVISO ROJO - PELIGRO EXTREMO"
                            elif nivel == 'naranja':
                                nivel_texto = "🟠 AVISO NARANJA - PELIGRO IMPORTANTE"
                            elif nivel == 'amarillo':
                                nivel_texto = "🟡 AVISO AMARILLO - RIESGO"
                            else:
                                continue
                            
                            mensaje = f"{nivel_texto}: {fenomeno}"
                            if descripcion:
                                descripcion_corta = descripcion[:100] + "..." if len(descripcion) > 100 else descripcion
                                mensaje += f" - {descripcion_corta}"
                            
                            alertas_procesadas.append(mensaje)
        
        if alertas_procesadas:
            print(f"✅ {len(alertas_procesadas)} alertas encontradas para {area}")
        else:
            print(f"✅ No hay alertas activas para {area}")
            
        return alertas_procesadas
        
    except Exception as e:
        print(f"ℹ Información de alertas no disponible para {area}: {e}")
        return []  # Importante: siempre devolver una lista, incluso vacía