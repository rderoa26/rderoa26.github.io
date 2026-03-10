# ================= config_ciudades.py =================
# Configuración específica para cada ciudad con sus destinatarios

CIUDADES = [
    {
        'nombre': 'Palencia',
        'municipio': '34120',
        'area_alertas': 'PAZ',
        'latitud': 42.00970,
        'longitud': -4.52890,
        'activa': True,
        'destinatarios': [
            'rderoa@gmail.com'
        ]
    },
    {
        'nombre': 'Valladolid',
        'municipio': '47186',
        'area_alertas': 'VAD',
        'latitud': 41.65200,
        'longitud': -4.72860,
        'activa': True,
        'destinatarios': [
            'rderoa@gmail.com'
        ]
    },
    {
        'nombre': 'Venta de Baños',
        'municipio': '34123',
        'area_alertas': 'PAZ',
        'latitud': 41.92140,
        'longitud': -4.49454,
        'activa': True,
        'destinatarios': [
            'rderoa@gmail.com'
        ]
    },
    {
        'nombre': 'Socuellamos',
        'municipio': '13078',
        'area_alertas': 'CRZ',
        'latitud': 39.29330,
        'longitud': -2.79417,
        'activa': True,  
        'destinatarios': [
            'rderoa@gmail.com',
            'inmajl50@gmail.com'
        ]
    },
]

def get_ciudades_activas():
    """Devuelve solo las ciudades activas"""
    return [c for c in CIUDADES if c.get('activa', True)]

def get_destinatarios_ciudad(ciudad_nombre):
    """Devuelve los destinatarios de una ciudad específica"""
    for ciudad in CIUDADES:
        if ciudad['nombre'] == ciudad_nombre:
            return ciudad.get('destinatarios', [])
    return []