from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.chataction import ChatAction
from telegram.ext import MessageHandler, Filters
from functools import wraps
import os, time
import datetime

updater = Updater(token='ADD YOUR TOKEN', use_context=True)
dispatcher = updater.dispatcher

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func

def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hey !!!\nDidn't get you please try again.")

@send_typing_action
def printp(update, context):
    """ Processing image """
    dt = datetime.datetime.now()
    updates = context.bot.get_updates()
    update.message.reply_text("Processing your image !!!")
    newFile = update.message.photo[-1].get_file()
    newFile.download('doc/{0}_{1}'.format(dt.strftime("%d%b%y_%H%M%S"), os.path.basename(newFile["file_path"])))

@send_typing_action
def doc(update, context):
    """ Processing documents """
    dt = datetime.datetime.now()
    updates = context.bot.get_updates()
    update.message.reply_text("Processing your document !!!")
    newFile = update.message.effective_attachment.get_file()
    newFile.download('doc/{0}_{1}'.format(dt.strftime("%d%b%y_%H%M%S"), os.path.basename(newFile["file_path"])))

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

start_handler = MessageHandler(Filters.photo, printp)
dispatcher.add_handler(start_handler)

start_handler = MessageHandler(Filters.document, doc)
dispatcher.add_handler(start_handler)

if __name__ == "__main__":
    updater.start_polling()
    updater.idle()
