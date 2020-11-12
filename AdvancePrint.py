from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.chataction import ChatAction
from telegram.ext import MessageHandler, Filters
from functools import wraps
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
import os, time
import datetime
import logging

COLOR, MORE, COPIES, SIZE, DUPLEX, TRAY = range(6)

default = {
    "color" : 0,
    "copies" : 1,
    "size" : "A4",
    "duplex" : 1,
    "tray" : 1,
    "doc_path" : "/home/pi/scripts/PrintBot/doc",
    "photo_path" : "/home/pi/scripts/PrintBot/photo",
    "default_file" : "/home/pi/scripts/PrintBot/config/default.cfg",
    "log_file" : "/home/pi/scripts/PrintBot/config/printBot.log"
}

def createConfig():
    with open(default["default_file"], 'w') as df:
        df.write("copies = " + str(default["copies"]) + "\n")
        df.write("color = " + str(default["color"]) + "\n")
        df.write("size = " + str(default["size"]) + "\n")
        df.write("duplex = " + str(default["duplex"]) + "\n")
        df.write("tray = " + str(default["tray"]) + "\n")

    log.info("Configuration file updated successfully")

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func

@send_typing_action
def photo(update, context):
    """ Processing image """
    dt = datetime.datetime.now()
    updates = context.bot.get_updates()
    reply_keyboard = [["B/W","Color"],["/cancel"]]
    update.message.reply_text("Nice Image !!\nYou want B/W or colored print ?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    newFile = update.message.photo[-1].get_file()
    newFile.download('doc/{0}_{1}'.format(dt.strftime("%d%b%y_%H%M%S"), os.path.basename(newFile["file_path"])))
    log.info("Photo received {0}".format(os.path.basename(newFile["file_path"])))
    
    return COLOR

@send_typing_action
def doc(update, context):
    """ Processing documents """
    dt = datetime.datetime.now()
    reply_keyboard = [["B/W","Color"],["/cancel"]]
    updates = context.bot.get_updates()
    update.message.reply_text("Processing your document !!!\nYou want B/W or colored print ?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    newFile = update.message.effective_attachment.get_file()
    newFile.download('doc/{0}_{1}'.format(dt.strftime("%d%b%y_%H%M%S"), os.path.basename(newFile["file_path"])))
    log.info("Document received {0}".format(os.path.basename(newFile["file_path"])))
    
    return COLOR
    
@send_typing_action
def copies(update, context):
    copy = update.message.text
    default["copies"] = int(copy)
    reply_keyboard = [["A4", "A3"], ["/cancel"]]
    update.message.reply_text("OK. You want {0} copies.\nPlease choose the paper size ?".format(copy),reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    log.info(f"No of copies : {copy}")
    return SIZE
    
@send_typing_action
def size(update, context):
    size = update.message.text
    default["size"] = size
    reply_keyboard = [["Single", "Double"], ["/cancel"]]
    update.message.reply_text("Paper size : {0}\nYou want single side or double side ?".format(size),reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    log.info(f"paper size choose {size}")
    return DUPLEX
    
@send_typing_action
def duplex(update, context):
    reply_keyboard = [["1","2","3"], ["/cancel"]]
    duples = update.message.text

    default["duplex"] = 0 if duples == "Single" else 1

    update.message.reply_text("OK. You want {0} side\nChoose the paper tray.".format(duples),reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    log.info(f"Duplex choosen is {duples}")
    return TRAY
    
@send_typing_action
def tray(update, context):
    tray = update.message.text
    default["tray"] = int(tray)
    update.message.reply_text("Paper will be choosen from tray {0}.\n\nPrinting with custom configuration...".format(tray))
    log.info(f"Paper tray will be {tray}")
    createConfig()
    return ConversationHandler.END

@send_typing_action
def more(update, context):
    _more = update.message.text

    if _more == "more":
        update.message.reply_text("Enter the no of copies you want.")
        log.info("More is choosen")
        return COPIES
    else:
        update.message.reply_text("Printing with default configuration....")
        log.info("No more choosen so default printing...")
        createConfig()
        return ConversationHandler.END

@send_typing_action
def color(update, context):
    reply_keyboard = [["more", "Print"], ["/cancel"]]
    color = update.message.text

    default["color"] = 0 if color == "B/W" else 1

    update.message.reply_text("Print will be in {0}\n\nChoose to print or want custom configurations ?".format(color),reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    log.info(f"Choosen color is {color}")
    return MORE

def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())
    log.warning("Cancel is pressed.")
    return ConversationHandler.END

def main():
    updater = Updater("ENTER YOUR TOKEN", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.photo, photo),
                     MessageHandler(Filters.document, doc)],

        states={
            COLOR: [MessageHandler(Filters.text, color),
                   CommandHandler('cancel', cancel)],

            MORE: [MessageHandler(Filters.text, more),
                   CommandHandler('cancel', cancel)],

            COPIES : [MessageHandler(Filters.text, copies),
                      CommandHandler('cancel', cancel)],
            
            SIZE: [MessageHandler(Filters.text, size),
                   CommandHandler('cancel', cancel)],
                      
            DUPLEX: [MessageHandler(Filters.text, duplex),
                   CommandHandler('cancel', cancel)],
                      
            TRAY: [MessageHandler(Filters.text, tray),
                   CommandHandler('cancel', cancel)],
           
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler,1)

    can_handler = CommandHandler('cancel', cancel)
    dp.add_handler(can_handler,2)

    can_handler = CommandHandler('cancel', cancel)
    dp.add_error_handler(can_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':

    logging.basicConfig(filename=default["log_file"], level=logging.INFO, format="[%(asctime)-8s] %(levelname)-8s : %(message)s")
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)-8s] %(levelname)-8s : %(message)s")
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    global log
    log = logging.getLogger()
    main()
