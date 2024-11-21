import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from tinydb import TinyDB, Query
import dictionary_response as dic

## t.me/ufrj_comissao_hc_bot
CHAVE_API = "7766028423:AAH7SCXbgT6UynPCNerhIbCigX-eIMBzW9g"
bot = telebot.TeleBot(CHAVE_API)

## Configuracoes do banco
DB_PATH = "db_alunos.json"
PDF_FOLDER = "pdfs"

# Garantir que a pasta exista
os.makedirs(PDF_FOLDER, exist_ok=True)

# Inicializar o banco de dados
db = TinyDB(DB_PATH)

# Armazenamento temporario para o fluxo da opcao1
user_data = {}

### BEGIN INSERIR HORAS ALUNO ###
@bot.message_handler(commands=["opcao1"])
def opcao1(msg):
    chat_id = msg.chat.id
    user_data[chat_id] = {'step': 'waiting_dre'}
    bot.send_message(chat_id, dic.opcao1_solicitar_dre)

def check_write_dre(msg):
    return user_data.get(msg.chat.id, {}).get('step') == 'waiting_dre'

@bot.message_handler(func=check_write_dre)
def handler_dre(msg):
    chat_id = msg.chat.id
    dre = msg.text
    user_data[chat_id]['dre'] = dre
    user_data[chat_id]['step'] = 'waiting_type'

    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(
        KeyboardButton("Estágio"), 
        KeyboardButton("Iniciação Científica"), 
        KeyboardButton("Projeto Extensão"),
        KeyboardButton("Ouvinte Eventos Científicos"),
        KeyboardButton("Apresentação Eventos Científicos"),
        KeyboardButton("Competição Acadêmicas"),
        KeyboardButton("Menção Honrosa"),
        KeyboardButton("Premiação acadêmica"),
        KeyboardButton("Representante discente"),
        KeyboardButton("Mesário"),
        KeyboardButton("Diretoria estudantil"),
        KeyboardButton("EJCM"),
        KeyboardButton("Organização de Eventos"),
        KeyboardButton("Monitor de Disciplina"),
        KeyboardButton("LCI"),
        KeyboardButton("Trabalho Comunitário"),
        KeyboardButton("Intercâmbio")
    )
    bot.send_message(chat_id, "Selecione o tipo de atividade: ", reply_markup=markup)
### END INSERIR HORAS ALUNO ###

def check(msg):
    return True

## Responde a saudacao, tem que ser o ultimo comando do codigo.
@bot.message_handler(func=check)
def response(msg):
    bot.reply_to(msg, dic.saudacao)

## Manter o bot ativo no telegram
bot.polling()