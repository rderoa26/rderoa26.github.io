# ================= iconos_utils.py =================
import os
from PIL import Image, ImageDraw

ICONOS = {
    "11": "☀️", "12": "🌤️", "13": "⛅", "14": "☁️", "15": "🌧️",
    "16": "⛈️", "17": "🌨️", "18": "🌦️", "19": "🌫️", "20": "💨",
    "21": "🌥️", "22": "🌧️☁️", "23": "☁️🌧️", "24": "🌨️☁️",
    "25": "⛈️🌧️", "26": "🌤️🌧️", "27": "🌙", "28": "☁️🌙", "29": "🌧️🌙",
}

MAPEO_TEXTOS = {
    "despejado": "☀️", "poco nuboso": "🌤️", "intervalos nubosos": "⛅",
    "nuboso": "☁️", "muy nuboso": "☁️☁️", "cubierto": "☁️☁️☁️",
    "lluvia": "🌧️", "lluvia escasa": "🌦️", "chubascos": "🌦️",
    "tormenta": "⛈️", "nieve": "🌨️", "niebla": "🌫️", "bruma": "🌫️",
    "calima": "🌫️", "viento": "💨", "granizo": "🌨️⚡", "helada": "❄️",
    "nubes y claros": "🌤️", "intervalos nubosos con lluvia": "⛅🌧️",
    "muy nuboso con lluvia": "☁️🌧️", "cubierto con lluvia": "☁️☁️🌧️",
    "nuboso con lluvia escasa": "☁️🌦️",
}

def obtener_icono_mejorado(codigo, descripcion):
    """Devuelve un icono específico basado en código y descripción"""
    if codigo in ICONOS:
        return ICONOS[codigo]
    
    desc_lower = descripcion.lower()
    
    for clave, icono in MAPEO_TEXTOS.items():
        if clave in desc_lower:
            return icono
    
    if "lluvia" in desc_lower and "nuboso" in desc_lower:
        if "muy nuboso" in desc_lower:
            return "☁️🌧️"
        elif "intervalos" in desc_lower:
            return "⛅🌧️"
        else:
            return "☁️🌧️"
    elif "lluvia" in desc_lower:
        return "🌧️"
    elif "nieve" in desc_lower:
        return "🌨️"
    elif "nuboso" in desc_lower or "nubes" in desc_lower:
        if "muy" in desc_lower:
            return "☁️☁️"
        elif "intervalos" in desc_lower:
            return "⛅"
        else:
            return "☁️"
    elif "despejado" in desc_lower:
        return "☀️"
    
    return "🌤️"

def obtener_icono_principal(tipo_semana):
    """Selecciona el icono para la tarjeta según el tipo de semana"""
    tipo = tipo_semana.lower()
    
    mapa = {
        "calor": "ola_calor.png", "cálida": "ola_calor.png",
        "fresca": "dias_frescos.png", "fría": "ola_frio.png",
        "templada": "semana_templada.png", "despej": "despejado.png",
        "parcial": "parcialmente_nublado.png", "nublado": "nublado.png",
        "lluvia": "lluvia_moderada.png", "tormenta": "tormenta.png",
        "nieve": "nieve.png", "helada": "nieve.png",
        "niebla": "niebla.png", "viento": "ventoso.png",
    }
    
    for clave, archivo in mapa.items():
        if clave in tipo:
            return os.path.join("iconos", archivo)
    
    return os.path.join("iconos", "parcialmente_nublado.png")

def cargar_icono_imagen(ruta, tamaño):
    """Carga un icono desde archivo o crea placeholder"""
    try:
        if not os.path.exists(ruta):
            icono = Image.new('RGBA', (tamaño, tamaño), (100, 100, 100, 200))
            draw = ImageDraw.Draw(icono)
            draw.ellipse([2, 2, tamaño-2, tamaño-2], fill=(150, 150, 150, 255))
            return icono
        
        icono = Image.open(ruta).convert("RGBA")
        return icono.resize((tamaño, tamaño), Image.LANCZOS)
    except:
        return Image.new('RGBA', (tamaño, tamaño), (100, 100, 100, 200))