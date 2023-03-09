import telebot
import random

# Inizializza il bot con il token fornito da BotFather
bot = telebot.TeleBot('YOURTOKEN')

# Memorizza gli utenti che partecipano al sorteggio in una lista
participants = []
is_closed = False
# ID del canale in cui inviare il messaggio per partecipare
channel_id = "@canale"

# Gestore per il comando /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, '/sorteggio per creare un un nuovo sorteggio\n/estrai per estrarre\n/partecipanti per vedere quanti partecipanti ci sono')

# Gestore per il comando /crea_sorteggio
@bot.message_handler(commands=['sorteggio'])
def create_raffle(message):
    global is_closed
    is_closed = False
    # Richiede al mittente del messaggio di inviare il titolo e la descrizione del sorteggio
    bot.reply_to(message, 'Invia il titolo del sorteggio:')
    bot.register_next_step_handler(message, get_raffle_title)

# Funzione per ottenere il titolo del sorteggio dal mittente del messaggio
def get_raffle_title(message):
    global title
    title = message.text
    bot.reply_to(message, 'Invia la descrizione del sorteggio:')
    bot.register_next_step_handler(message, get_raffle_description)

# Funzione per ottenere la descrizione del sorteggio dal mittente del messaggio
def get_raffle_description(message):
    global description
    #description = message.text
    description = f"Invita 2 amici ad entrare nel nostro canale prima di partecipare_ \(fai degli screen con orario e giorno evidenti per avere delle prove dell'invito dei tuoi amici altrimenti in caso di vincita verrai scartato\)_ per poter vincere *{title}*\!\nLink canale : {channel_id}"
    bot.reply_to(message, f'Hai creato il sorteggio "{title}" con la descrizione "{description}".')
    # Invia il messaggio per partecipare al canale specificato
    bot.send_message(channel_id, f'Partecipa al sorteggio *{title}*\n\n{description}\n_Entra cliccando il pulsante qui sotto:_', reply_markup=get_inline_keyboard(), parse_mode='MarkdownV2')

# Funzione per creare la tastiera inline con il pulsante per partecipare
def get_inline_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    participate_button = telebot.types.InlineKeyboardButton(text='Partecipa', callback_data='partecipa')
    keyboard.add(participate_button)
    return keyboard

@bot.callback_query_handler(func=lambda call: call.data == 'partecipa')
def participate_inline(call):
    global is_closed
    if is_closed:
        # Se il sorteggio è chiuso, non è possibile partecipare
        bot.answer_callback_query(callback_query_id=call.id, text='Mi dispiace, il sorteggio è già chiuso.')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'Partecipa al sorteggio *{title}*\n\n{description}\n\n_*SORTEGGIO CHIUSO*_\n\n\.', parse_mode='MarkdownV2')
        return
    # Aggiunge l'utente alla lista dei partecipanti se non è già presente
    if call.from_user.id not in participants:
        participants.append(call.from_user.id)
        # Invia un messaggio di conferma all'utente che ha cliccato sul pulsante inline
        bot.answer_callback_query(callback_query_id=call.id, text='Hai partecipato al sorteggio!')
        # Aggiorna il messaggio nel canale con il numero di partecipanti attuali
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'Partecipa al sorteggio *{title}*\n\n{description}\n_Entra cliccando il pulsante qui sotto:_\n\nAttualmente ci sono {len(participants)} partecipanti\.', reply_markup=get_inline_keyboard(), parse_mode='MarkdownV2')
    else:
        # Invia un messaggio di errore all'utente che ha già partecipato al sorteggio
        bot.answer_callback_query(callback_query_id=call.id, text='Sei già dentro al sorteggio!')

@bot.message_handler(commands=['estrai'])
def extract_winner(message):
    global is_closed
    is_closed = True
    # Verifica se ci sono abbastanza partecipanti per estrarre un vincitore
    if len(participants) >= 1:
        winner_id = random.choice(participants)
        winner = bot.get_chat(winner_id)
        bot.reply_to(message, f'Il vincitore del sorteggio è {winner.first_name} {winner.last_name} (@{winner.username})!')
        # Rimuove tutti i partecipanti dalla lista
        participants.clear()
        # Invia un messaggio nel canale per informare che il sorteggio è stato completato
        bot.send_message(channel_id, f'Il sorteggio *{title}* è stato completato\!\n\n*Il vincitore è @{winner.username}\.*\n\n_Contatta_ @tua_per poter ritirare il premio\!_', parse_mode='MarkdownV2')
    else:
        bot.reply_to(message, 'Non ci sono abbastanza partecipanti per estrarre un vincitore!')


@bot.message_handler(commands=['partecipanti'])
def show_participants(message):
    global participants
    if not participants:
        bot.reply_to(message, "Non ci sono partecipanti al sorteggio.")
        return
    bot.reply_to(message, f"I partecipanti sono {len(participants)}\nLista dei partecipanti:\n{participants}")

bot.polling()

