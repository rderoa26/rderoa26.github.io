# ================= config.py =================
# Configuración GLOBAL del proyecto

# ===== EMAIL (servidor) =====
# Estos datos son los mismos para TODAS las ciudades
EMAIL_FROM = "rderoa@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_PASS = "ylfh ffmi kuib fhbp"

# ===== AEMET (clave API) =====
API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJyZGVyb2FAZ21haWwuY29tIiwianRpIjoiZTQzZTNkODgtM2JkMi00ZTVhLWJjZTAtZDhiYzA3NDEzOGMzIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE3NTg0NDA4NzMsInVzZXJJZCI6ImU0M2UzZDg4LTNiZDItNGU1YS1iY2UwLWQ4YmMwNzQxMzhjMyIsInJvbGUiOiIifQ.FKAIBl9r9gwUPFkhaKYfbsDCGpWieDo8fwSNKPcEJvo"

# ===== RUTAS =====
RUTA_ICONOS = "iconos"
RUTA_TEMPLATES = "templates"

# ===== CONFIGURACIÓN DE MÓDULOS ACTIVOS =====
MODULOS_ACTIVOS = {
    'aemet': True,
    'graficos': True,
    'tarjeta': True,
    'curiosidades': {
        'activo': True,
        'fuentes': {
            'base_local': True,
            'refranes': False,
            'cine_musica': False,
            'cocina': False,
        }
    }
}

# ===== CONFIGURACIÓN DE CURIOSIDADES AVANZADAS =====
CURIOSIDADES_CONFIG = {
    'activo': True,
    'fuentes': {
        'base_local': True,
        'refranes': True,        # Peso 4 (muy popular)
        'cine_musica': True,      # Peso 2
        'cocina': True,           # Peso 3 (popular)
        'numeros': True,          # Peso 1
        'citas': True,            # Peso 2
        'naturaleza': True,       # Peso 3 (muy popular)
        'mascotas': True,         # Peso 3 (encanta)
        'sol': True,              # Peso 2
    }
}

# URL de APIs
API_URLS = {
    'numbers': "http://numbersapi.com/random/trivia",
    'mealdb': "https://www.themealdb.com/api/json/v1/1/random.php",
    'quotegarden': "https://quote-garden.onrender.com/api/v3/quotes/random",
    'catfact': "https://catfact.ninja/fact",
    'dogceo': "https://dog.ceo/api/breeds/image/random",
    'sunrise': "https://api.sunrise-sunset.org/json",
}

# ===== LOCALE =====
import locale
try:
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
except:
    try:
        locale.setlocale(locale.LC_TIME, "es_ES")
    except:
        print("⚠ No se pudo establecer locale en español")