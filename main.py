import telebot
import os
from claude_api import Client
from telebot import types

cookie = os.environ.get('cookie')
claude_api = Client(cookie)

# Reemplaza 'YOUR_BOT_TOKEN' con el token de tu bot de Telegram
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Verifica si la variable de entorno BOT_TOKEN está definida
if BOT_TOKEN is None:
    raise ValueError("La variable de entorno BOT_TOKEN no está definida.")

# Crea una instancia del bot de Telegram
bot = telebot.TeleBot(BOT_TOKEN)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

@bot.message_handler(content_types=['document'])
def receive_text_file(message):
    # Verifica si el archivo 'hola.txt' ya existe
    file_path = os.path.join(BASE_DIR, 'transcription.txt')
    if os.path.exists(file_path):
        # Si existe, elimina el archivo existente
        os.remove(file_path)
    
    # Guarda el nuevo archivo 'transcription.txt' en la carpeta principal
    if message.document.file_name == 'transcription.txt':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, "Archivo en proceso")
        prompt = "Resume"
        conversation_id = claude_api.create_new_chat()['uuid']
        response = claude_api.send_message(prompt, conversation_id, attachment="transcription.txt", timeout=600)
        print(response)
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "El archivo no es 'transcription.txt', no se guardará.")

# Inicia el bucle de polling
bot.infinity_polling()
