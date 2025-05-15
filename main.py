import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from logger import logger
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
user_states = {} # State of users
DATA_FILE = 'data.json'

def load_titles():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading titles: {e}")
        return {}

def save_titles(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Error saving titles: {e}")
        return False

# handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("The bot is starting")
    except Exception as e:
        logger.error(f"Error in start handler function: {e}")
        return

async def handle_add_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        user_states[user_id] = 'ADD'
        msg = """
        لطفاً عنوان آگهی خود را با فرمت زیر ارسال کنید        
        عنوان آگهی - لینک صفحه آگهی - لینک صفحه دیوار

        """
        await update.message.reply_text(msg)
    except Exception as e:
        logger.error(f"Error in handle_add_cmd function: {e}")
        return

async def handle_delete_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        data = load_titles()
        titles = [i[2] for i in data.get(user_id, [])]
        if not titles:
            return await update.message.reply_text('عنوانی برای حذف وجود ندارد.')
        buttons = [[InlineKeyboardButton(t, callback_data=f'delete|{t}')] for t in titles]
        markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text('عنوان مورد نظر را انتخاب کنید:', reply_markup=markup)
    except Exception as e:
        logger.error(f"Error in handle_delete_cmd function: {e}")
        return

async def handle_my_ads_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        data = load_titles()
        titles = [i[2] for i in data.get(user_id, [])]
        if not titles:
            await update.message.reply_text('آگهی وجود ندارد.')
            return
        msg = "آگهی های شما :" + "\n" + "\n".join(titles)
        await update.message.reply_text(msg)
    except Exception as e:
        logger.error(f"Error in handle_delete_cmd function: {e}")
        return

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        user_id = str(query.from_user.id)
        action, title = query.data.split('|', 1)

        if action == 'delete':
            data = load_titles()
            for d in data[user_id]:
                if title == d[2]:
                    data[user_id].remove(d)
                    save_titles(data)
                    await query.edit_message_text('عنوان با موفقیت حذف شد.')
                    return
            await query.edit_message_text('عنوان یافت نشد.')
    except Exception as e:
        logger.error(f"Error in handle_callback function: {e}")
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        state = user_states.get(user_id)
        if state == 'ADD':
            title = update.message.text
            title = [s.strip() for s in title.split('-')]
            if len(title) != 3:
                await update.message.reply_text('فرمت آگهی نادرست است. لطفاً دوباره امتحان کنید.')
                return
            data = load_titles()
            data.setdefault(user_id, []).append(title)
            save_titles(data)
            user_states[user_id] = None
            await update.message.reply_text(f'عنوان "{title[2]}" ذخیره شد.')
        else:
            await update.message.reply_text('عملیات مورد نظر یافت نشد.')
    except Exception as e:
        logger.error(f"Error in handle_message function: {e}")
        return


async def task(context: ContextTypes.DEFAULT_TYPE):
    try:
        data = load_titles()
        for user_id, ads in data.items():
            try:
                await context.bot.send_message(chat_id=int(user_id), text='پیام زمان‌بندی‌شده: این اعلان هر یک ساعت ارسال می‌شود.')
            except Exception as e:
                print(f"خطا در ارسال پیام زمان‌بندی‌شده به {user_id}: {e}")
    except Exception as e:
        print(f"Error in task function: {e}")


def main():
    try:
        application = ApplicationBuilder().token(BOT_TOKEN).build()

        # set handlers
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('add', handle_add_cmd))
        application.add_handler(CommandHandler('delete', handle_delete_cmd))
        application.add_handler(CommandHandler('my_ads', handle_my_ads_cmd))
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        
        # run scraper every hour
        application.job_queue.run_repeating(task, interval=3600, first=0)

        
        # run bot
        application.run_webhook(
            listen='127.0.0.1',
            port=5000,
            url_path=BOT_TOKEN,
            webhook_url=f'https://diwar.loca.lt/{BOT_TOKEN}',
        )
    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == '__main__':
    main()
