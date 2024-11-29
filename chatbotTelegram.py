import os
import glob
import telebot
from enum import Enum
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from tinydb import TinyDB, Query
from dotenv import load_dotenv

import dictionary_response as dic
from send_email import send_email_with_attachment

# Status da solicitacao
class Status(Enum):
    ANDAMENTO = 1
    APROVADO = 2
    REPROVADO = 3

# Carregar variáveis de ambiente
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Token do Bot
KEY_ACCESS = os.getenv("KEY_ACCESS") # Token da comissão

## t.me/ufrj_comissao_hc_bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

## Configuracoes dos bancos e pastas
DB_HORAS = "db_horas_alunos.json"
DB_SOLICITACAO = "db_solicitacao_alunos.json"

## Configuracoes das pastas
PDF_FOLDER = "pdfs"
FORM_FOLDER = "forms"

# Garantir que a pasta exista
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(FORM_FOLDER, exist_ok=True)

# Inicializar o banco de dados
db_horas = TinyDB(DB_HORAS)
db_solicitacao = TinyDB(DB_SOLICITACAO)
query = Query()

# Armazenamento temporario para o fluxo da opcao1
user_data = {}
solicitacao_data = {}
comissao_data = {}

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

def check_write_type(msg):
    return user_data.get(msg.chat.id, {}).get('step') == 'waiting_type'

@bot.message_handler(func=check_write_type)
def handler_type(msg):
    chat_id = msg.chat.id
    type = msg.text
    user_data[chat_id]['type'] = type
    user_data[chat_id]['step'] = 'waiting_pdf'
    bot.send_message(chat_id, "Por favor, envie o PDF que comprove a atividade.")

def check_write_pdf(msg):
    return user_data.get(msg.chat.id, {}).get('step') == 'waiting_pdf'

@bot.message_handler(content_types=['document'], func=check_write_pdf)
def handler_pdf(msg):
    chat_id = msg.chat.id
    document = msg.document

    if document.mime_type != 'application/pdf':
        bot.send_message(chat_id, "O arquivo enviado não é um PDF. Por favor, envie um PDF válido.")
        return
    
    # Salvar o arquivo na pasta
    dre = user_data[chat_id]['dre']
    type = user_data[chat_id]['type']
    file_info = bot.get_file(document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = f"{dre}_{type}_{chat_id}.pdf"
    file_path = os.path.join(PDF_FOLDER, file_name)
    with open(file_path, "wb") as f:
        f.write(downloaded_file)

    # Salvar os dados no TinyDB
    db_horas.insert({
        'chat_id': chat_id,
        'dre': user_data[chat_id]['dre'],
        'atividade': user_data[chat_id]['type'],
        'pdf_caminho': file_path
    })

    # Finalizar o fluxo
    bot.send_message(chat_id, "Obrigado! Seus dados foram recebidos com sucesso. Caso deseje voltar ao menu digite novamente.")
    del user_data[chat_id]
### END INSERIR HORAS ALUNO ###

### BEGIN SOLICITACAO INCLUSAO HORAS ###
@bot.message_handler(commands=["opcao2"])
def opcao2(msg):
    chat_id = msg.chat.id
    solicitacao_data[chat_id] = {'step': 'waiting_dre'}
    bot.send_message(chat_id, dic.opcao1_solicitar_dre)

def check_write_dre_sol(msg):
    return solicitacao_data.get(msg.chat.id, {}).get('step') == 'waiting_dre'

@bot.message_handler(func=check_write_dre_sol)
def handler_dre_sol(msg):
    chat_id = msg.chat.id
    dre = msg.text
    solicitacao = db_solicitacao.search(query.dre == dre)

    if len(solicitacao) > 0:
        bot.send_message(chat_id, dic.existe_solicitacao)
        del solicitacao_data[chat_id]
        return

    solicitacao_data[chat_id]['dre'] = dre
    solicitacao_data[chat_id]['step'] = 'waiting_name'
    bot.send_message(chat_id, "Informe seu nome completo: ")

def check_write_name(msg):
    return solicitacao_data.get(msg.chat.id, {}).get('step') == 'waiting_name'

@bot.message_handler(func=check_write_name)
def handler_name_sol(msg):
    chat_id = msg.chat.id
    name = msg.text
    solicitacao_data[chat_id]['name'] = name
    solicitacao_data[chat_id]['step'] = 'waiting_email'
    bot.send_message(chat_id, "Informe seu nome email institucional (@dcc): ")

def check_write_email(msg):
    return solicitacao_data.get(msg.chat.id, {}).get('step') == 'waiting_email'

@bot.message_handler(func=check_write_email)
def handler_email_sol(msg):
    chat_id = msg.chat.id
    email = msg.text
    solicitacao_data[chat_id]['email'] = email
    solicitacao_data[chat_id]['step'] = 'waiting_form'

    bot.send_message(chat_id, "Por favor, envie o formulário preenchido e assinado.")

def check_write_form(msg):
    return solicitacao_data.get(msg.chat.id, {}).get('step') == 'waiting_form'

@bot.message_handler(content_types=['document'], func=check_write_form)
def handler_form_sol(msg):
    chat_id = msg.chat.id
    document = msg.document

    ## Salvar arquivo
    dre = solicitacao_data[chat_id]['dre']
    name = solicitacao_data[chat_id]['name']
    email = solicitacao_data[chat_id]['email']
    file_info = bot.get_file(document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = f"{dre}_{document.file_name}"
    file_path = os.path.join(PDF_FOLDER, file_name)
    with open(file_path, "wb") as f:
        f.write(downloaded_file)

    bot.send_message(chat_id, "Obrigado! Estamos enviando seus dados para comissão. Ao finalizar avisamos!")

    # Pegar os comprovantes do aluno
    padrao = os.path.join(PDF_FOLDER, f'{dre}_*.pdf') 
    # Lista todos os arquivos que correspondem ao padrão 
    arquivos_comprovante = glob.glob(padrao)
    
    success = send_email_with_attachment(file_path, arquivos_comprovante, name, dre, email)
    if(success):
        db_solicitacao.insert({
            'chat_id': chat_id,
            'dre': dre,
            'name': name,
            'email': email,
            'pdf_caminho': file_path,
            'status': Status.ANDAMENTO.value,
            'observation': ''
        })
        bot.send_message(chat_id, "Solicitação enviada com sucesso para a comissão. ")
    else:
        bot.send_message(chat_id, "Não foi possível enviar o seu formulário. Tenten novamente.")
        os.remove(file_path)

    del solicitacao_data[chat_id]
### END SOLICITACAO INCLUSAO HORAS ###

### BEGIN VER ANDAMENTO ###
@bot.message_handler(commands=["opcao3"])
def opcao3(msg):
    chat_id = msg.chat.id
    solicitacao_data[chat_id] = {'step': 'andamento_dre'}
    bot.send_message(chat_id, dic.opcao1_solicitar_dre)

def check_write_andamento(msg):
    return solicitacao_data.get(msg.chat.id, {}).get('step') == 'andamento_dre'

@bot.message_handler(func=check_write_andamento)
def handler_dre_sol(msg):
    chat_id = msg.chat.id
    dre = msg.text
    alunos = db_solicitacao.search(query.dre == dre)
    if len(alunos) <= 0:
        bot.send_message(chat_id, dic.sem_solicitacao)

    aluno = alunos[0]
    name_status = Status(aluno['status']).name
    text = f'*Nome*: {aluno['name']} \n *DRE*: {aluno['dre']} \n *Situação*: {name_status} \n *Observação*: {aluno['observation']}'
    bot.send_message(chat_id, text, parse_mode="Markdown")
### END VER ANDAMENTO ###

### BEGIN LISTAR ATIVIDADES ###
@bot.message_handler(commands=["opcao4"])
def opcao4(msg):
    chat_id = msg.chat.id
    user_data[chat_id] = {'step': 'listing_activity'}
    bot.send_message(chat_id, dic.opcao1_solicitar_dre)

def check_listing_activity(msg):
    return user_data.get(msg.chat.id, {}).get('step') == 'listing_activity'

@bot.message_handler(func=check_listing_activity)
def handler_dre_activity(msg):
    chat_id = msg.chat.id
    dre = msg.text
    activity = db_horas.search(query.dre == dre)

    if len(activity) <= 0:
        bot.send_message(chat_id, dic.no_registered_activities)
        return
    
    lista = "Listagem: \n" 
    for item in activity: 
        lista += f"- *Atividade:* {item['atividade']}, *Comprovante:* {item['pdf_caminho']}\n"
    bot.send_message(chat_id, lista, parse_mode="Markdown")
### END LISTAR ATIVIDADES ###

### BEGIN COMISSAO ACESSO ###
@bot.message_handler(commands=["comissao"])
def acesso_comissao(msg):
    chat_id = msg.chat.id
    comissao_data[chat_id] = {'step': 'waiting_key_access'}
    bot.reply_to(msg, "Por favor, informe a chave de acesso: ")

def check_write_access(msg):
    return comissao_data.get(msg.chat.id, {}).get('step') == 'waiting_key_access'

@bot.message_handler(func=check_write_access)
def handler_acesso_comissao(msg):
    chat_id = msg.chat.id
    key_access = msg.text

    if key_access != KEY_ACCESS:
        bot.send_message(chat_id, dic.acesso_negado)
        return
    
    comissao_data[chat_id]['step'] = 'access_success'
    bot.send_message(chat_id, dic.opcoes_comissao)

def check_pendente(msg):
    chat_id = msg.chat.id
    is_access = comissao_data.get(chat_id, {}).get('step') == 'access_success'
    
    if(is_access == False):
        bot.send_message(chat_id, dic.acesso_negado)
    
    return is_access

@bot.message_handler(commands=['pendentes'], func=check_pendente)
def handler_pendente(msg):
    chat_id = msg.chat.id
    pendentes = db_solicitacao.search(query.status == Status.ANDAMENTO.value)
    lista = "Listagem: \n" 
    for aluno in pendentes: 
        lista += f"- *Nome*: {aluno['name']}, *DRE*: {aluno['dre']}\n"
    bot.send_message(chat_id, lista, parse_mode="Markdown")

@bot.message_handler(commands=['aprovar_aluno'], func=check_pendente)
def handler_aprovar(msg):
    chat_id = msg.chat.id
    bot.send_message(chat_id, dic.opcao1_solicitar_dre)
    comissao_data[chat_id]['step2'] = 'comissao_dre_aprovar'

def check_dre_aprover(msg):
    chat_id = msg.chat.id
    is_access = comissao_data.get(chat_id, {}).get('step') == 'access_success'
    is_aprover = comissao_data.get(chat_id, {}).get('step2') == 'comissao_dre_aprovar'
    
    if(is_access == False or is_aprover == False):
        bot.send_message(chat_id, dic.acesso_negado)
    
    return is_access

@bot.message_handler(func=check_dre_aprover)    
def handler_aprovar_dre(msg):  
    chat_id = msg.chat.id  
    dre = msg.text
    db_solicitacao.update({'status': Status.APROVADO.value}, query.dre == dre)
    bot.send_message(chat_id, dic.aluno_aprovado)
    del comissao_data[chat_id]

@bot.message_handler(commands=['reprovar_aluno'], func=check_pendente)
def handler_reprovado(msg):
    chat_id = msg.chat.id
    bot.send_message(chat_id, dic.opcao1_solicitar_dre)
    comissao_data[chat_id]['step2'] = 'comissao_dre_reprover'

def check_dre_reprover(msg):
    chat_id = msg.chat.id
    is_access = comissao_data.get(chat_id, {}).get('step') == 'access_success'
    is_reprover = comissao_data.get(chat_id, {}).get('step2') == 'comissao_dre_reprover'
    
    if(is_access == False or is_reprover == False):
        bot.send_message(chat_id, dic.acesso_negado)
    
    return is_access

@bot.message_handler(func=check_dre_reprover)   
def handler_reprovar_dre(msg): 
    chat_id = msg.chat.id
    dre = msg.text
    db_solicitacao.update({'status': Status.REPROVADO.value}, query.dre == dre)
    comissao_data[chat_id]['is_reprovado'] = True
    comissao_data[chat_id]['dre'] = dre
    bot.send_message(chat_id, dic.aluno_reprovado_obs)
    del comissao_data[chat_id]

def check_write_obs(msg):
    chat_id = msg.chat.id
    is_access = comissao_data.get(chat_id, {}).get('step') == 'access_success'
    is_obs = comissao_data.get(chat_id, {}).get('is_reprovado') == True
    
    if(is_access == False and is_obs is None):
        bot.send_message(chat_id, dic.acesso_negado)
    
    return is_access

@bot.message_handler(func=check_write_obs)
def handler_reprovacao_obs(msg):
    chat_id = msg.chat.id
    obs = msg.text
    dre = comissao_data[chat_id]['dre']
    db_solicitacao.update({'observation': obs}, query.dre == dre)
    bot.send_message(chat_id, dic.aluno_reprovado)

@bot.message_handler(commands=['sair_acesso'], func=check_pendente)
def handler_sair(msg):
    chat_id = msg.chat.id
    bot.send_message(chat_id, dic.comissao_sair)
    del comissao_data[chat_id]
### END COMISSAO ACESSO ###

def check(msg):
    return True

## Responde a saudacao, tem que ser o ultimo comando do codigo.
@bot.message_handler(func=check)
def response(msg):
    bot.reply_to(msg, dic.saudacao)

## Manter o bot ativo no telegram
bot.polling()