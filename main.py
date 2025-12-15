from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from flask import Flask
from threading import Thread
import json

# =================== CONFIGURACIÓN ===================
import os
TOKEN = os.getnev (8514212882:AAH8bybuxrcd1FoqFViLjf01fRgh96WX8ls)
ADMIN_CHAT_ID = int(os.getnev(1492731368))
DATABASE_FILE = "database.json"

# =================== FUNCIONES DE BASE DE DATOS ===================
def load_data():
    try:
        with open(DATABASE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATABASE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =================== COMANDOS ===================
def start(update: Update, context: CallbackContext):
    update.message.reply_text("¡Bienvenido al Pick3 Bot! Usa /registrar para comenzar.")

def registrar(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    data = load_data()
    if user_id not in data:
        data[user_id] = {"name": update.effective_user.first_name, "creditos": 100, "jugadas": []}
        save_data(data)
        update.message.reply_text("¡Registrado! Tienes 100 créditos iniciales.")
    else:
        update.message.reply_text("Ya estás registrado.")

def saldo(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    data = load_data()
    if user_id in data:
        update.message.reply_text(f"Tienes {data[user_id]['creditos']} créditos.")
    else:
        update.message.reply_text("Primero regístrate con /registrar.")

def jugar(update: Update, context: CallbackContext):
    if len(context.args) != 1 or not context.args[0].isdigit() or len(context.args[0]) != 3:
        update.message.reply_text("Uso: /jugar 123 (tres dígitos)")
        return

    numero = context.args[0]
    user_id = str(update.effective_user.id)
    data = load_data()

    if user_id not in data:
        update.message.reply_text("Primero regístrate con /registrar")
        return

    if data[user_id]["creditos"] < 10:
        update.message.reply_text("No tienes suficientes créditos (costo 10).")
        return

    data[user_id]["creditos"] -= 10
    data[user_id]["jugadas"].append(numero)
    save_data(data)

    update.message.reply_text(f"¡Número {numero} registrado! Te quedan {data[user_id]['creditos']} créditos.")

    # Notificación al admin
    admin_message = f"{data[user_id]['name']} ha jugado el número {numero}."
    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)

def jugadas(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    data = load_data()
    if user_id not in data:
        update.message.reply_text("Primero regístrate con /registrar")
        return

    jugadas_usuario = data[user_id]["jugadas"]
    if not jugadas_usuario:
        update.message.reply_text("No has jugado ningún número en este sorteo.")
    else:
        numeros = ", ".join(jugadas_usuario)
        total = len(jugadas_usuario)
        update.message.reply_text(f"Has jugado {total} número(s): {numeros}")

def ranking(update: Update, context: CallbackContext):
    data = load_data()
    if not data:
        update.message.reply_text("No hay jugadores registrados.")
        return
    sorted_users = sorted(data.items(), key=lambda x: x[1]['creditos'], reverse=True)
    mensaje = "🏆 Ranking de créditos:\n"
    for user_id, info in sorted_users:
        mensaje += f"{info['name']}: {info['creditos']} créditos\n"
    update.message.reply_text(mensaje)

def reset(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id != str(ADMIN_CHAT_ID):
        update.message.reply_text("Solo el administrador puede usar /reset.")
        return

    data = load_data()
    for user in data:
        data[user]["jugadas"] = []
    save_data(data)
    update.message.reply_text("Todas las jugadas del sorteo han sido reiniciadas.")

def ayuda(update: Update, context: CallbackContext):
    mensaje = (
        "Comandos disponibles:\n"
        "/registrar - Registrarte y recibir créditos iniciales\n"
        "/saldo - Ver tus créditos\n"
        "/jugar <numero> - Jugar un número (3 dígitos)\n"
        "/jugadas - Ver tus jugadas actuales\n"
        "/ranking - Ver ranking de créditos\n"
        "/reset - Reiniciar jugadas (solo admin)\n"
        "/ayuda - Mostrar este mensaje"
    )
    update.message.reply_text(mensaje)

# =================== CONFIGURAR TELEGRAM BOT ===================
updater = Updater(TOKEN)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("registrar", registrar))
dp.add_handler(CommandHandler("saldo", saldo))
dp.add_handler(CommandHandler("jugar", jugar))
dp.add_handler(CommandHandler("jugadas", jugadas))
dp.add_handler(CommandHandler("ranking", ranking))
dp.add_handler(CommandHandler("reset", reset))
dp.add_handler(CommandHandler("ayuda", ayuda))

# =================== SERVIDOR WEB PARA RENDER/UptimeRobot ===================
app = Flask('')

@app.route('/')
def home():
    return "Bot despierto!"

def run():
    app.run(host='0.0.0.0', port=8080)

t = Thread(target=run)
t.start()

# =================== INICIAR BOT ===================
updater.start_polling()
updater.idle()
