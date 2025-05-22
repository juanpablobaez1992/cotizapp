from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging

# ---- CONFIG ----
COMISION_PORCENTAJE = 0.15   # Comisión 15%
ENVIO_USD_POR_KG = 40.0      # Envío por kilo
DOLAR_BLUE = 1300
DOLAR_MEP = 1200

# ---- LOG ----
logging.basicConfig(level=logging.INFO)

# ---- ESTADO POR USUARIO ----
usuarios = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    usuarios[user_id] = {"paso": "nombre"}
    await update.message.reply_text("¡Manso saludo, culiao! Empecemos la cotización. Decime el *nombre del producto*, bro.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mensaje = update.message.text.strip()
    
    if user_id not in usuarios:
        usuarios[user_id] = {"paso": "nombre"}
        await update.message.reply_text("Arranquemos de nuevo. Decime el *nombre del producto*, bro.")
        return

    estado = usuarios[user_id]

    if estado["paso"] == "nombre":
        estado["nombre"] = mensaje
        estado["paso"] = "link"
        await update.message.reply_text("Buenísimo. Ahora pasame el *link del producto*, culiao.")
    
    elif estado["paso"] == "link":
        estado["link"] = mensaje
        estado["paso"] = "peso"
        await update.message.reply_text("Zarpado. ¿Cuánto pesa en *kilos* el producto, bro?")
    
    elif estado["paso"] == "peso":
        try:
            limpio = mensaje.replace(",", ".").replace("kg", "").strip()
            estado["peso"] = float(limpio)
            estado["paso"] = "precio"
            await update.message.reply_text("Tremendo. Ahora decime el *precio en dólares* del producto (sin el $).")
        except ValueError:
            await update.message.reply_text("Epa, eso no parece un número. Mandame el *peso en kg*, bro.")
    
    elif estado["paso"] == "precio":
        try:
            limpio = mensaje.replace("$", "").replace(",", ".").strip()
            estado["precio"] = float(limpio)
            respuesta = calcular_cotizacion_mendocina(
                estado["nombre"], estado["link"], estado["peso"], estado["precio"]
            )
            await update.message.reply_text(respuesta)  # <-- no usamos Markdown para evitar errores
            del usuarios[user_id]
        except ValueError:
            await update.message.reply_text("Cuidado culiao, el *precio* tiene que ser un número. Probá de nuevo.")
    
    else:
        usuarios[user_id] = {"paso": "nombre"}
        await update.message.reply_text("Arranquemos de cero. Decime el *nombre del producto*.")

def calcular_cotizacion_mendocina(nombre, link, peso, precio_usd):
    comision = precio_usd * COMISION_PORCENTAJE
    envio = peso * ENVIO_USD_POR_KG
    total_usd = precio_usd + comision + envio
    total_ars_mep = total_usd * DOLAR_MEP
    total_ars_blue = total_usd * DOLAR_BLUE

    return f"""
🛒 {nombre}
🔗 {link}

📦 Peso: {peso} kg
💵 Precio base: USD {precio_usd:.2f}
🔧 Comisión (15%): USD {comision:.2f}
🚚 Envío estimado: USD {envio:.2f}

🔥 Total final: USD {total_usd:.2f}
💸 En pesos MEP: ${total_ars_mep:,.0f}
💸 En pesos Blue: ${total_ars_blue:,.0f}

_Alta ganga, bro. Esta cotización está mansa como vino de finca, culiao._
"""

# ---- MAIN ----
if __name__ == '__main__':
    TOKEN = '7980979040:AAEFgs12B1waa76HO28A-In5mbNbxLWBp4c'  # <-- pegá el token de BotFather
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Cotizapp Mendocino funcionando... 🍷")
    app.run_polling()
