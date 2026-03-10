# ================= graficos.py =================
import matplotlib.pyplot as plt
from io import BytesIO
import matplotlib
matplotlib.use('Agg')

def generar_graficas(df):
    """Genera las gráficas de temperaturas y lluvia"""
    print("📊 Generando gráficas...")
    
    buffers = {}
    
    # Gráfica de temperaturas
    fig_temp, ax1 = plt.subplots(figsize=(8, 4))
    ax1.plot(df["fecha"], df["tmax"], marker="o", linewidth=2, label="Máxima", color="red")
    ax1.plot(df["fecha"], df["tmin"], marker="o", linewidth=2, label="Mínima", color="blue")
    ax1.set_ylabel("Temperatura (°C)")
    ax1.set_xlabel("Fecha")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_title("Evolución de temperaturas", fontsize=14, fontweight="bold")
    fig_temp.autofmt_xdate()
    fig_temp.tight_layout()
    
    buffer_temp = BytesIO()
    fig_temp.savefig(buffer_temp, format="png", dpi=100, bbox_inches="tight")
    buffer_temp.seek(0)
    buffers['temp'] = buffer_temp
    buffers['temp_fig'] = fig_temp
    
    # Gráfica de lluvia
    fig_lluvia, ax2 = plt.subplots(figsize=(8, 4))
    bars = ax2.bar(df["fecha"], df["lluvia"], color="skyblue", edgecolor="steelblue", alpha=0.8)
    ax2.set_ylabel("Probabilidad de lluvia (%)")
    ax2.set_xlabel("Fecha")
    ax2.set_ylim(0, 105)
    ax2.grid(True, axis="y", alpha=0.3)
    ax2.set_title("Probabilidad de lluvia diaria", fontsize=14, fontweight="bold")
    
    for bar, value in zip(bars, df["lluvia"]):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
                 f'{value}%', ha='center', va='bottom', fontsize=10)
    
    fig_lluvia.autofmt_xdate()
    fig_lluvia.tight_layout()
    
    buffer_lluvia = BytesIO()
    fig_lluvia.savefig(buffer_lluvia, format="png", dpi=100, bbox_inches="tight")
    buffer_lluvia.seek(0)
    buffers['lluvia'] = buffer_lluvia
    buffers['lluvia_fig'] = fig_lluvia
    
    print("✔ Gráficas generadas")
    return buffers

def cerrar_graficas(buffers):
    """Cierra las figuras para liberar memoria"""
    plt.close(buffers['temp_fig'])
    plt.close(buffers['lluvia_fig'])