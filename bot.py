import random
import os
import telebot
import subprocess
from pydub import AudioSegment
from dbhelper import DBHelper
import time

db =DBHelper()

from telebot.types import Message
TOKEN = "Your token should be here"
STIKER_ID = "CAACAgIAAxkBAAMbX5gjaZuUIbBkdKbYV7DZ92wxN8wAAhoAA8A2TxOC27C1PAZBVxsE"

bot = telebot.TeleBot(TOKEN)

USERS = set()

db.setup()

default_text = "Hello my friends. Я многоязычный синтез построенный на tacotron. Шла саша по шоссе и сосала сушку"

def generate_TTP(voice_id = "ex", text = default_text ):

    path_demo = 'C:\Docs\Companies\SDAML(NSU)\Test_task\\baseline\Multi-Tacotron-Voice-Cloning-Telegram-bot\demo_cli.py'
    output_path = "output\{}.wav".format(voice_id)

    subprocess.run( 'python {} -p "input\{}.wav" -p2 "{}" -t "{}" --no_sound'.format(path_demo,
                                                                                    voice_id,
                                                                                    output_path,
                                                                                    text),
                                                                                    shell=True)

    time.sleep(2)
    wav_output = AudioSegment.from_file(output_path, format='wav')
    wav_output.export('reply\\{}.ogg'.format(voice_id), format='ogg')

    #remove temporary file
#     time.sleep(2)
#     os.remove(output_path)
#     print(output_path,'has been removed')

@bot.message_handler(commands=['start', 'help'])
def command_hendler(message: Message):
    reply ="""
Привет! Я бот, который учится клонировать русскую речь. \n
1. Если хочешь, чтобы я клонировал твой голос, то запиши для 
меня голосовое сообщение длительность 5-10 секунд(«с чувством, с толком, с...)))) 
Когда я закончу процесс обработки, отправлю тебе голосовое с клонированным голосом.\n
2. Я запоминаю голоса, поэтому если хочешь озвучить предложение клонированным голосом, то
просто напиши мне его.\n
3. Если хочешь обновить голос, достаточно снова отправить голосовое сообщение. Но смотри, что предыдущий
'голосовой экземпляр' я удалю.\n
( По дефолту я пользуюсь сторонним голосом)
            """

    bot.reply_to(message, reply)



@bot.message_handler(content_types=['voice'])
def generate_voice(message: Message):

    chat_id = message.chat.id
    voice_id = hash(str(chat_id))

    db.add_voice(chat_id, voice_id)



    voice_info = bot.get_file(message.voice.file_id)
    downloaded_voice = bot.download_file((voice_info.file_path))

    orig_path = "input\\{}.ogg".format(voice_id)

    with open(orig_path, 'wb') as a:
        a.write(downloaded_voice)

    ogg_voice = AudioSegment.from_file(orig_path, format="ogg")
    ogg_voice.export("input\\{}.wav".format(voice_id), format="wav")
    # we don't need original.ogg anymore
    os.remove(orig_path)

    #generate our voice
    generate_TTP(voice_id)

    #send our voice message
    voice = open('reply\\{}.ogg'.format(voice_id), 'rb')
    bot.send_voice(message.chat.id, voice)
    #os.remove('reply\\{}.ogg'.format(voice_id))

@bot.message_handler(content_types=['text'])
def generate_voice_from_text(message: Message):

    voice_id = db.get_voice(message.chat.id)[-1]
    print(voice_id,' this is voice_id from fb' )
    generate_TTP(voice_id, message.text)
    # sendVoice
    voice = open('reply\\{}.ogg'.format(voice_id), 'rb')
    bot.send_voice(message.chat.id, voice)
    os.remove('reply\\{}.ogg'.format(voice_id))


@bot.message_handler(content_types=['sticker'])
def sticker_handler(message: Message):
    bot.send_sticker(message.chat.id, STIKER_ID)




# @bot.inline_handler(lambda query: query.query)
# def query_text(inline_query):
#     print(inline_query)
#     # Query message is text


bot.polling(timeout=60)