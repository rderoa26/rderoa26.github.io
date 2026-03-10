# ================= main.py =================
import sys
import os
import re
import time
from datetime import datetime
from io import BytesIO
from jinja2 import Template

# Asegurar que podemos importar nuestros módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
import config_ciudades
import aemet
import graficos
import tarjeta
import email_utils
from iconos_utils import obtener_icono_mejorado
from curiosidades import gestor as curiosidades

# ================= FUNCIONES DE CÁLCULO =================

def calcular_resumen(df):
    """Calcula todos los resúmenes y alertas"""
    
    num_dias = len(df)
    max_abs = df["tmax"].max()
    min_abs = df["tmin"].min()
    media_periodo = (df["tmax"].mean() + df["tmin"].mean()) / 2
    dias_lluvia = (df["lluvia"] > 50).sum()
    
    # Episodios destacados
    dias_bajo_cero = (df["tmin"] < 0).sum()
    dias_muy_calor = (df["tmax"] >= 35).sum()
    dias_lluviosos = (df["lluvia"] >= 60).sum()
    
    # Determinar tipo de semana
    if media_periodo >= 30:
        tipo_semana = "Semana muy calurosa"
        icono_resumen = "ola_calor.png"
    elif media_periodo >= 22:
        tipo_semana = "Semana cálida"
        icono_resumen = "despejado.png"
    elif media_periodo >= 12:
        tipo_semana = "Semana templada"
        icono_resumen = "semana_templada.png"
    elif media_periodo >= 5:
        tipo_semana = "Semana fresca"
        icono_resumen = "dias_frescos.png"
    else:
        tipo_semana = "Semana fría"
        icono_resumen = "ola_frio.png"
    
    episodio = tipo_semana
    color_fondo = "#f4f6f8"
    icono_principal = "🌤"
    tam_icono = "26px"
    
    if dias_bajo_cero >= 3:
        episodio = "Episodio de frío con heladas"
        color_fondo = "#e6f2ff"
        icono_principal = "❄"
        tam_icono = "40px"
    elif dias_muy_calor >= 3:
        episodio = "Episodio de calor intenso"
        color_fondo = "#fff3e6"
        icono_principal = "🔥"
        tam_icono = "40px"
    
    return {
        'num_dias': num_dias,
        'max_abs': max_abs,
        'min_abs': min_abs,
        'media_periodo': media_periodo,
        'dias_lluvia': dias_lluvia,
        'dias_bajo_cero': dias_bajo_cero,
        'dias_muy_calor': dias_muy_calor,
        'dias_lluviosos': dias_lluviosos,
        'tipo_semana': tipo_semana,
        'icono_resumen': icono_resumen,
        'episodio': episodio,
        'color_fondo': color_fondo,
        'icono_principal': icono_principal,
        'tam_icono': tam_icono
    }

def construir_alertas(df, resumen, alertas_oficiales):
    """Construye las alertas para email y tarjeta"""
    
    alertas_email = []
    
    # Alertas oficiales
    for alerta in alertas_oficiales:
        alertas_email.append(f"🚨 {alerta}")
    
    # Alertas generales
    if resumen['dias_bajo_cero'] >= 3:
        alertas_email.append("🥶 Episodio de frío destacado con varias heladas.")
    elif resumen['dias_bajo_cero'] >= 2:
        alertas_email.append("❄ Varias heladas en la semana.")
    
    if resumen['dias_muy_calor'] >= 3:
        alertas_email.append("🔥 Episodio de calor intenso.")
    elif resumen['dias_muy_calor'] >= 2:
        alertas_email.append("☀ Varios días muy calurosos.")
    
    if resumen['dias_lluviosos'] >= 4:
        alertas_email.append("🌧 Semana inestable con lluvias frecuentes.")
    
    # Alertas diarias
    for _, r in df.iterrows():
        if r["lluvia"] >= 70:
            alertas_email.append(
                f"🌧️ Lluvia {r['fecha'].strftime('%A %d')} ({r['lluvia']}%)"
            )
        if r["tmin"] <= 2:
            alertas_email.append(
                f"❄️ Helada {r['fecha'].strftime('%A %d')} ({r['tmin']}°C)"
        )
        
        # Extraer velocidad del viento
        match = re.search(r"\d+", r["viento"])
        viento_kmh = int(match.group()) if match else 0
        if viento_kmh >= 40:
            alertas_email.append(
                f"💨 Viento fuerte {r['fecha'].strftime('%A %d')} ({viento_kmh} km/h)"
            )
    
    # Alertas para tarjeta (formato conciso)
    alertas_generales_tarjeta = []
    alertas_diarias_tarjeta = []
    
    if resumen['dias_bajo_cero'] >= 3:
        alertas_generales_tarjeta.append("Episodio de frío")
    elif resumen['dias_bajo_cero'] >= 2:
        alertas_generales_tarjeta.append("Varias heladas")
    
    if resumen['dias_muy_calor'] >= 3:
        alertas_generales_tarjeta.append("Episodio de calor")
    
    if resumen['dias_lluviosos'] >= 4:
        alertas_generales_tarjeta.append("Semana lluviosa")
    
    for _, r in df.iterrows():
        if r["lluvia"] >= 80:
            alertas_diarias_tarjeta.append(
                f"Lluvia {r['fecha'].strftime('%a')} {r['lluvia']}%"
            )
        if r["tmin"] <= 1:
            alertas_diarias_tarjeta.append(
                f"Helada {r['fecha'].strftime('%a')} {r['tmin']}°C"
            )
    
    return alertas_email, alertas_generales_tarjeta, alertas_diarias_tarjeta

def generar_html(df, resumen, alertas_email, ciudad_nombre):
    """Genera el contenido HTML del email para una ciudad"""
    
    template_path = os.path.join('templates', 'email_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template_str = f.read()
    
    template = Template(template_str)
    
    return template.render(
        df=df,
        obtener_icono_mejorado=obtener_icono_mejorado,
        alertas_email=alertas_email,
        ciudad=ciudad_nombre,
        color_fondo=resumen['color_fondo'],
        icono_principal=resumen['icono_principal'],
        tam_icono=resumen['tam_icono'],
        episodio=resumen['episodio'],
        max_abs=resumen['max_abs'],
        min_abs=resumen['min_abs'],
        media_periodo=resumen['media_periodo'],
        dias_lluvia=resumen['dias_lluvia'],
        num_dias=resumen['num_dias'],
        fecha_generacion=datetime.now().strftime("%d/%m/%Y %H:%M")
    )

def generar_texto_plano(ciudad_nombre, resumen, alertas_email):
    """Genera la versión texto plano del email"""
    
    texto = f"""
Previsión del tiempo - 7 días ({ciudad_nombre})
Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}

{resumen['episodio']}
================================
Temperatura máxima: {resumen['max_abs']}°C
Temperatura mínima: {resumen['min_abs']}°C
Temperatura media: {resumen['media_periodo']:.1f}°C
Días con lluvia: {resumen['dias_lluvia']} de {resumen['num_dias']}

AVISOS IMPORTANTES:
{chr(10).join(['- ' + a for a in alertas_email]) if alertas_email else '- No hay avisos'}

ARCHIVOS ADJUNTOS:
- tarjeta_{ciudad_nombre}.png
- temperaturas_{ciudad_nombre}.png
- lluvia_{ciudad_nombre}.png
"""
    return texto

def procesar_una_ciudad(ciudad_info):
    """Procesa una única ciudad y devuelve los datos para enviar"""
    
    print(f"\n{'='*60}")
    print(f"🏙️  PROCESANDO CIUDAD: {ciudad_info['nombre']}")
    print(f"📧 Destinatarios: {len(ciudad_info['destinatarios'])}")
    print(f"{'='*60}")
    
    # 1. Obtener datos de AEMET
    dias = aemet.obtener_prediccion(ciudad_info['municipio'])
    if not dias:
        print(f"❌ Error obteniendo datos para {ciudad_info['nombre']}")
        return None
        
    df = aemet.procesar_datos(dias)
    alertas_oficiales = aemet.obtener_alertas_oficiales(ciudad_info['area_alertas'])
    
    # 2. Calcular resúmenes
    resumen = calcular_resumen(df)
    
    # 3. Construir alertas
    alertas_email, alertas_gral_tarjeta, alertas_diarias_tarjeta = construir_alertas(
        df, resumen, alertas_oficiales
    )
    
    # 4. Generar gráficas
    buffers_graficos = graficos.generar_graficas(df)
    
    # 5. Generar tarjeta
    print("🖼️ Generando tarjeta resumen...")
    imagen_tarjeta = tarjeta.generar_tarjeta(
        ciudad_info['nombre'],
        resumen['tipo_semana'],
        resumen['icono_resumen'],
        resumen['max_abs'],
        resumen['min_abs'],
        resumen['media_periodo'],
        resumen['dias_lluvia'],
        alertas_gral_tarjeta,
        alertas_diarias_tarjeta,
        alertas_oficiales
    )
    
    # 6. Generar HTML
    html_content = generar_html(df, resumen, alertas_email, ciudad_info['nombre'])
    
    # 7. Obtener curiosidad
    print("🎁 Añadiendo curiosidad del día...")
    curiosidad = curiosidades.obtener_curiosidad_del_dia()
    html_curiosidad, texto_curiosidad = curiosidades.formatear_curiosidad_para_email(curiosidad)
    html_content = html_content.replace('<!-- CURIOSIDAD_DIA -->', html_curiosidad)
    
    # 8. Preparar texto plano
    texto_plano = generar_texto_plano(ciudad_info['nombre'], resumen, alertas_email)
    texto_plano += texto_curiosidad
    
    return {
        'ciudad': ciudad_info['nombre'],
        'destinatarios': ciudad_info['destinatarios'],
        'html': html_content,
        'texto_plano': texto_plano,
        'buffers': buffers_graficos,
        'tarjeta': imagen_tarjeta,
        'alertas_oficiales': alertas_oficiales
    }

def enviar_para_una_ciudad(resultado):
    """Envía emails a TODOS los destinatarios de una ciudad"""
    
    print(f"\n📧 Enviando emails para {resultado['ciudad']}...")
    print(f"   Destinatarios: {len(resultado['destinatarios'])}")
    
    # Preparar los adjuntos comunes (una vez por ciudad)
    buffer_tarjeta = BytesIO()
    resultado['tarjeta'].save(buffer_tarjeta, format="PNG")
    buffer_tarjeta.seek(0)
    
    enviados = 0
    total = len(resultado['destinatarios'])
    
    for idx, destinatario in enumerate(resultado['destinatarios'], 1):
        print(f"   📨 {idx}/{total} - {destinatario}")
        
        # Crear mensaje para este destinatario
        asunto = f"🌤️ Previsión - {resultado['ciudad']} - {datetime.now().strftime('%d/%m/%Y')}"
        msg = email_utils.crear_mensaje_base(asunto, destinatario)
        
        # Adjuntar partes
        msg_alternative = email_utils.crear_alternativa(
            resultado['texto_plano'], 
            resultado['html']
        )
        msg.attach(msg_alternative)
        
        # Adjuntar gráficas (inline)
        email_utils.adjuntar_imagen(msg, resultado['buffers']['temp'], "temp")
        email_utils.adjuntar_imagen(msg, resultado['buffers']['lluvia'], "lluvia")
        
        # Adjuntar como archivos (con nombre personalizado)
        resultado['buffers']['temp'].seek(0)
        email_utils.adjuntar_imagen(
            msg, resultado['buffers']['temp'], None, 
            f"temperaturas_{resultado['ciudad']}.png", inline=False
        )
        
        resultado['buffers']['lluvia'].seek(0)
        email_utils.adjuntar_imagen(
            msg, resultado['buffers']['lluvia'], None, 
            f"lluvia_{resultado['ciudad']}.png", inline=False
        )
        
        # Adjuntar tarjeta
        buffer_tarjeta.seek(0)
        email_utils.adjuntar_imagen(
            msg, buffer_tarjeta, None,
            f"tarjeta_{resultado['ciudad']}.png", inline=False
        )
        
        # Enviar
        if email_utils.enviar_email_individual(msg, destinatario):
            enviados += 1
        
        # Pequeña pausa entre envíos para no saturar Gmail
        if idx < total:
            time.sleep(1)
    
    return enviados, total

def main():
    print("🚀 INICIANDO PROCESO MULTICIUDAD")
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Obtener lista de ciudades activas
    ciudades = config_ciudades.get_ciudades_activas()
    
    # Calcular total de destinatarios
    total_destinatarios = sum(len(c['destinatarios']) for c in ciudades)
    
    print(f"📍 Ciudades activas: {len(ciudades)}")
    print(f"👥 Total destinatarios: {total_destinatarios}")
    print("\n📋 Lista de ciudades y destinatarios:")
    for c in ciudades:
        print(f"   • {c['nombre']}: {len(c['destinatarios'])} destinatario(s)")
    
    resultados = []
    
    # Procesar cada ciudad
    for idx, ciudad in enumerate(ciudades, 1):
        print(f"\n📌 Procesando {idx}/{len(ciudades)}")
        
        resultado = procesar_una_ciudad(ciudad)
        if resultado:
            resultados.append(resultado)
            
            # Pausa entre ciudades
            if idx < len(ciudades):
                print("⏳ Pausa de 3 segundos antes de siguiente ciudad...")
                time.sleep(3)
    
    # Enviar emails
    print(f"\n{'='*60}")
    print("📧 ENVIANDO EMAILS")
    print(f"{'='*60}")
    
    total_enviados = 0
    total_esperados = 0
    
    for resultado in resultados:
        enviados, esperados = enviar_para_una_ciudad(resultado)
        total_enviados += enviados
        total_esperados += esperados
        time.sleep(2)  # Pausa entre ciudades
    
    # Resumen final
    print(f"\n{'='*60}")
    print("✅ PROCESO COMPLETADO")
    print(f"{'='*60}")
    print(f"📍 Ciudades procesadas: {len(resultados)}/{len(ciudades)}")
    print(f"👥 Emails enviados: {total_enviados}/{total_esperados}")
    
    if total_enviados < total_esperados:
        print(f"⚠  Fallos: {total_esperados - total_enviados}")

if __name__ == "__main__":
    main()