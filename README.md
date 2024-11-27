# chat-hc-geti
Criação de um chatbox para orientar alunos e comissão nas horas complementares da UFRJ

## REQUISITOS:
- python 3.12.4
- pip [já vem quando você baixa o python]
- TinyDB
- dotenv
- pyTelegramBotAPI

## EXECUÇÃO:
i) Adicione no seu .env:
- TELEGRAM_TOKEN -> está no telegram do grup, procure :)
- KEY_ACCESS -> está no telegram do grup, procure :)
- EMAIL_USER -> use um email
- EMAIL_PASSWORD -> use um email
- RECIPIENT_EMAIL -> use um email

ii) Execute o arquivo "chatbotTelegram.py"

iii) Ao executar acesse o bot no telegram: t.me/ufrj_comissao_hc_bot

iv) Teste o fluxo XD

## Opções aluno:
Para alunos temos as seguintes opções:
- /opcao1 = gravar os comprovantes de atividades e as atividades desenvolvidas dos alunos.
- /opcao2 = aluno solicita a inclusão das horas no boletim. Ao finalizar o bot envia os dados para o email da comissão [o email no .env]
- /opcao3 = aluno analisa o andamento da sua solicitação

## Opções Comissão:
Para a comissão consiga ter acesso aos dados de atividades dos alunos ele precisa digitar "/comissao" e passar o token de acesso [no .env]. Quando o acesso for aprovado terá as opções:
- /pendentes = listar os alunos que estão em andamento de solicitação, exibindo nome e dre dos alunos pendentes.
- /aprovar_aluno = passando o dre do aluno o seu status é atualizado para aprovado.
- /reprovar_aluno = passando o dre do aluno o seu status é atualizado para reprovado e adicionado o motivo da reprovação.
- sair_acesso = sair do fluxo da comissão
