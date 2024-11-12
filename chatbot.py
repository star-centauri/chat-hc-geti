from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer ## Treinar pergunta e resposta
from chatterbot.trainers import ChatterBotCorpusTrainer  ## Para treinar com corpus

bot = ChatBot(
    'ChatBotHC', # Identificador so chat
    read_only = True, # para ele nao aprender com o que o usuario digita
    preprocessors=[
        'chatterbot.preprocessors.convert_to_ascii', # Remove caracteres especiais
        'chatterbot.preprocessors.unescape_html', # Ignora html
        'chatterbot.preprocessors.clean_whitespace' # Limpa os espaços extras
    ], 
    logic_adapters = [{
        'import_path': 'chatterbot.logic.BestMatch',
        'default_response': 'Desculpe, não consigo processar sua solicitação. Tente novamente.',
        'maximum_similarity_threshold': 0.90
    }],
    database_uri='sqlite:///database.sqlite3',  # Salva o progresso do treinamento
)

trainer = ListTrainer(bot)

# SAUDACOES #
trainer.train([
    "Olá",
    "Bom dia! Em que posso ser útil?",
    "Sou o ChatBotHC, seu assistente virtual.",
])

# Treinamento com corpus em português (recomendado para mais precisão)
corpus_trainer = ChatterBotCorpusTrainer(bot)
corpus_trainer.train("chatterbot.corpus.portuguese")

# Testar resposta do bot
response = bot.get_response('Olá, bom dia!')
print("Bot Response:", response)
