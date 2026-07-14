import telebot
from telebot import types
import os
from dotenv import load_dotenv
from database import init_db, salvar_cliente, salvar_solicitacao

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(TOKEN)
user_states = {}
user_data = {}

init_db()

def main_menu(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("📢 Como funciona", callback_data="como_funciona"))
    markup.add(types.InlineKeyboardButton("💰 Tabela de preços", callback_data="precos"))
    markup.add(types.InlineKeyboardButton("📝 Solicitar análise", callback_data="solicitar_analise"))
    markup.add(types.InlineKeyboardButton("📊 Meus pedidos", callback_data="meus_pedidos"))
    markup.add(types.InlineKeyboardButton("❓ Dúvidas", callback_data="duvidas"))
    markup.add(types.InlineKeyboardButton("👨‍💼 Falar com suporte", callback_data="suporte"))
    
    bot.send_message(chat_id, "👋 *Bem-vindo ao atendimento de divulgações!*\n\n"
                              "Escolha uma opção abaixo para continuar:", 
                     reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🎉 Olá! Seja bem-vindo ao nosso canal de divulgações.")
    main_menu(message.chat.id)
# ====================== CALLBACKS ======================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data

    if data == "como_funciona":
        texto = ("📢 *Como funciona:*\n\n"
                 "1️⃣ Preencha o formulário de análise\n"
                 "2️⃣ Nossa equipe avalia em até 48h\n"
                 "3️⃣ Se aprovado → Pagamento via PIX\n"
                 "4️⃣ Publicamos no dia combinado\n\n"
                 "✅ Alcance médio: +50.000 pessoas")
        bot.send_message(chat_id, texto, parse_mode="Markdown")
        main_menu(chat_id)

    elif data == "precos":
        texto = ("💰 *Tabela de Preços:*\n\n"
                 "• Post Simples (1 imagem) → R$ 97\n"
                 "• Post + Story → R$ 147\n"
                 "• Pacote 3 posts → R$ 247\n"
                 "• Divulgação em destaque → R$ 397\n\n"
                 "🔹 Preços promocionais para primeira divulgação!")
        bot.send_message(chat_id, texto, parse_mode="Markdown")
        main_menu(chat_id)

    elif data == "solicitar_analise":
        user_states[user_id] = "nome_empresa"
        user_data[user_id] = {}
        bot.send_message(chat_id, "📝 *Vamos começar a análise da sua divulgação*\n\n"
                                  "Qual é o **nome da empresa**?")

    elif data == "meus_pedidos":
        bot.send_message(chat_id, "📊 Você ainda não tem pedidos. Faça sua primeira solicitação!")
        main_menu(chat_id)

    elif data == "duvidas":
        bot.send_message(chat_id, "❓ Qual é sua dúvida? Envie uma mensagem que vamos te responder.")
        main_menu(chat_id)

    elif data == "suporte":
        bot.send_message(chat_id, "👨‍💼 Fale diretamente com o suporte:\n@seuusername")

# ====================== FORMULÁRIO ======================
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text

    if user_id not in user_states:
        return

    state = user_states[user_id]

    if state == "nome_empresa":
        user_data[user_id]['nome_empresa'] = text
        user_states[user_id] = "responsavel"
        bot.send_message(chat_id, "Qual é o nome do responsável pela empresa?")

    elif state == "responsavel":
        user_data[user_id]['responsavel'] = text
        user_states[user_id] = "whatsapp"
        bot.send_message(chat_id, "Qual é o WhatsApp para contato? (com DDD)")

    elif state == "whatsapp":
        user_data[user_id]['whatsapp'] = text
        user_states[user_id] = "instagram"
        bot.send_message(chat_id, "Qual é o Instagram da empresa? (@username)")

    elif state == "instagram":
        user_data[user_id]['instagram'] = text
        user_states[user_id] = "site"
        bot.send_message(chat_id, "Tem site? (opcional - digite 'não' se não tiver)")

    elif state == "site":
        user_data[user_id]['site'] = text if text.lower() != "não" else ""
        user_states[user_id] = "nicho"
        bot.send_message(chat_id, "Qual é o nicho da sua empresa? (ex: moda, beleza, alimentação...)")

    elif state == "nicho":
        user_data[user_id]['nicho'] = text
        user_states[user_id] = "objetivo"
        bot.send_message(chat_id, "Qual é o objetivo da campanha? (ex: aumentar vendas, divulgar novo produto...)")

    elif state == "objetivo":
        user_data[user_id]['objetivo'] = text
        user_states[user_id] = "descricao"
        bot.send_message(chat_id, "Descreva o que você deseja divulgar:")

    elif state == "descricao":
        user_data[user_id]['descricao'] = text
        user_states[user_id] = "logo"
        bot.send_message(chat_id, "Envie a logo da empresa (como imagem):")

    elif state == "logo":
        if message.photo:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded = bot.download_file(file_info.file_path)
            logo_path = f"media/logo_{user_id}.jpg"
            with open(logo_path, 'wb') as f:
                f.write(downloaded)
            user_data[user_id]['logo_path'] = logo_path

            bot.send_message(chat_id, "✅ Logo recebida!\n\nEnvie uma imagem ou vídeo adicional (opcional). Se não quiser, digite 'pronto'.")
            user_states[user_id] = "midia"
        else:
            bot.send_message(chat_id, "Por favor, envie uma imagem da logo.")

    elif state == "midia":
        if text and text.lower() == "pronto":
            finalizar_solicitacao(chat_id, user_id)
        elif message.photo or message.video:
            # Salvar mídia (simplificado)
            finalizar_solicitacao(chat_id, user_id)
        else:
            finalizar_solicitacao(chat_id, user_id)

def finalizar_solicitacao(chat_id, user_id):
    dados = user_data.get(user_id, {})
    if not dados.get('nome_empresa'):
        return

    cliente_id = salvar_cliente(user_id, dados)
    solicitacao_id = salvar_solicitacao(cliente_id, dados.get('descricao'), dados.get('logo_path'))

    bot.send_message(chat_id, "✅ *Solicitação enviada com sucesso!*\n\n"
                              "Nossa equipe fará a análise e retornará em breve.", parse_mode="Markdown")
    
    # Notificação para o admin (você)
    bot.send_message(chat_id, "🔍 Uma nova solicitação foi enviada para análise.")
    
    del user_states[user_id]
    if user_id in user_data:
        del user_data[user_id]
    
    main_menu(chat_id)

# ====================== INICIAR BOT ======================
if __name__ == "__main__":
    print("🤖 Bot de atendimento iniciado...")
    bot.infinity_polling()
# ... (continuo no próximo mensagem com o resto do código)
