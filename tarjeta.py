# ================= tarjeta.py =================
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
from iconos_utils import obtener_icono_principal, cargar_icono_imagen
from config import RUTA_ICONOS

def crear_fondo_degradado(ancho, alto, color_top, color_bottom):
    """Crea un fondo con degradado vertical"""
    fondo = Image.new("RGB", (ancho, alto), color_top)
    draw = ImageDraw.Draw(fondo)

    for y in range(alto):
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * y / alto)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * y / alto)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * y / alto)
        draw.line([(0, y), (ancho, y)], fill=(r, g, b))

    return fondo

def dibujar_texto_multilinea_con_ancho_maximo(draw, texto, x, y, fuente, ancho_maximo, color="black", espacio_linea=5):
    """Dibuja texto con control de ancho máximo"""
    palabras = texto.split()
    lineas = []
    linea_actual = ""

    for palabra in palabras:
        prueba = linea_actual + " " + palabra if linea_actual else palabra
        ancho_texto = draw.textlength(prueba, font=fuente)

        if ancho_texto <= ancho_maximo:
            linea_actual = prueba
        else:
            if linea_actual:
                lineas.append(linea_actual)
            linea_actual = palabra

    if linea_actual:
        lineas.append(linea_actual)

    for linea in lineas:
        ancho_linea = draw.textlength(linea, font=fuente)
        if ancho_linea > ancho_maximo:
            try:
                fuente_pequena = ImageFont.truetype("arial.ttf", fuente.size - 4)
            except:
                fuente_pequena = fuente
            draw.text((x, y), linea, font=fuente_pequena, fill=color)
        else:
            draw.text((x, y), linea, font=fuente, fill=color)
        
        y += fuente.size + espacio_linea

    return y

def generar_tarjeta(ciudad, tipo_semana, icono_resumen, max_abs, min_abs, 
                   media_periodo, dias_lluvia, alertas_generales, 
                   alertas_diarias, alertas_oficiales):
    """Genera una tarjeta resumen en imagen"""
    
    ancho = 800
    alto = 2400
    margen = 40
    x_texto = margen + 40
    margen_derecho = ancho - margen - 80
    
    # Crear tarjeta blanca interior
    tarjeta = Image.new("RGB", (ancho - margen*2, alto - margen*2), "white")

    # Fondo degradado
    imagen = crear_fondo_degradado(
        ancho, alto,
        (230, 240, 255),  # azul claro
        (255, 255, 255)   # blanco
    )

    # Sombra
    sombra = Image.new("RGB", (ancho - margen*2, alto - margen*2), "black")
    sombra = sombra.filter(ImageFilter.GaussianBlur(25))
    imagen.paste(sombra, (margen+10, margen+10))
    imagen.paste(tarjeta, (margen, margen))

    draw = ImageDraw.Draw(imagen)

    # Cargar fuentes
    try:
        fuente_titulo = ImageFont.truetype("arial.ttf", 60)
        fuente_grande = ImageFont.truetype("arial.ttf", 50)
        fuente_resumen = ImageFont.truetype("arial.ttf", 48)
        fuente_normal = ImageFont.truetype("arial.ttf", 42)
        fuente_media = ImageFont.truetype("arial.ttf", 38)
        fuente_pequena = ImageFont.truetype("arial.ttf", 32)
    except:
        fuente_titulo = fuente_grande = fuente_resumen = fuente_normal = fuente_media = fuente_pequena = ImageFont.load_default()

    # Icono grande principal
    ruta_icono = obtener_icono_principal(tipo_semana)
    icono_grande = cargar_icono_imagen(ruta_icono, 180)
    imagen.paste(icono_grande, (int(ancho/2 - 90), 40), icono_grande)

    y = 230

    # Título
    draw.text((ancho/2, y), "Previsión 7 días", font=fuente_titulo, fill="black", anchor="mm")
    y += 120

    # Ciudad
    draw.text((ancho/2, y), ciudad, font=fuente_grande, fill="black", anchor="mm")
    y += 140
    
    # Resumen
    texto_resumen = f"Resumen: {tipo_semana}"
    ruta_icono_resumen = os.path.join(RUTA_ICONOS, icono_resumen)
    
    if os.path.exists(ruta_icono_resumen):
        icono = Image.open(ruta_icono_resumen).convert("RGBA").resize((60, 60), Image.LANCZOS)
        bbox = draw.textbbox((0, 0), texto_resumen, font=fuente_resumen)
        ancho_texto = bbox[2] - bbox[0]
        bloque_ancho = ancho_texto + 70
        inicio_x = (ancho - bloque_ancho) // 2
        imagen.paste(icono, (inicio_x, y - 30), icono)
        draw.text((inicio_x + 70, y), texto_resumen, font=fuente_resumen, fill="black")

    y += 120

    # Datos numéricos
    color_max = "red" if max_abs >= 30 else "black"
    color_min = "blue" if min_abs <= 0 else "black"

    draw.text((x_texto, y), f"Máx prevista: {max_abs}°C", font=fuente_normal, fill=color_max)
    y += 80
    draw.text((x_texto, y), f"Mín prevista: {min_abs}°C", font=fuente_normal, fill=color_min)
    y += 80
    draw.text((x_texto, y), f"Media semana: {round(media_periodo,1)}°C", font=fuente_normal, fill="black")
    y += 80
    draw.text((x_texto, y), f"Días con lluvia fuerte: {dias_lluvia}", font=fuente_normal, fill="black")
    y += 120

    # Alertas oficiales
    if alertas_oficiales:
        y += 20
        icono_alerta = cargar_icono_imagen(os.path.join(RUTA_ICONOS, "tormenta.png"), 45)
        if icono_alerta:
            imagen.paste(icono_alerta, (x_texto, y), icono_alerta)
        draw.text((x_texto + 55, y), "⚠️ AVISOS OFICIALES", font=fuente_media, fill="darkred")
        y += 60
        
        for alerta in alertas_oficiales[:3]:  # Máximo 3 alertas
            alerta_corta = alerta
            if "PELIGRO EXTREMO" in alerta:
                alerta_corta = alerta.replace("🔴 AVISO ROJO - PELIGRO EXTREMO", "🔴 ROJO")
            elif "PELIGRO IMPORTANTE" in alerta:
                alerta_corta = alerta.replace("🟠 AVISO NARANJA - PELIGRO IMPORTANTE", "🟠 NARANJA")
            
            y = dibujar_texto_multilinea_con_ancho_maximo(
                draw, alerta_corta, x_texto + 45, y, fuente_pequena, margen_derecho - x_texto, "darkred"
            )
            y += 15
        y += 20

    # Recomendaciones
    todas_alertas = [("general", a) for a in alertas_generales] + [("diaria", a) for a in alertas_diarias[:8]]
    
    if todas_alertas:
        y += 20
        icono_aviso = cargar_icono_imagen(os.path.join(RUTA_ICONOS, "advertencia.png"), 35)
        if icono_aviso:
            imagen.paste(icono_aviso, (x_texto, y+2), icono_aviso)
        draw.text((x_texto + 45, y), "AVISOS DESTACADOS", font=fuente_media, fill="red")
        y += 70

        for tipo, alerta in todas_alertas:
            if tipo == "diaria" and len(alerta) > 25:
                alerta = (alerta.replace("jueves", "ju.").replace("viernes", "vi.")
                              .replace("sábado", "sá.").replace("domingo", "do."))
            
            y = dibujar_texto_multilinea_con_ancho_maximo(
                draw, alerta, x_texto + 35, y, fuente_pequena, margen_derecho - x_texto - 10, "black"
            )
            y += 15

    # Si no hay alertas
    if not alertas_oficiales and not todas_alertas:
        y += 30
        draw.text((x_texto, y), "✅ Sin avisos destacados", font=fuente_normal, fill="green")
        y += 60

    # Recortar al contenido real
    imagen = imagen.crop((0, 0, ancho, min(y + 100, alto)))
    
    return imagen