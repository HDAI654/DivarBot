import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler
from logger import logger
import os
from dotenv import load_dotenv
from Tools import tools
from scraper import scrape_data

load_dotenv()

TITLE, LINK_PAGE, LINK_AD = range(3)
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
PORT = int(os.getenv("PORT"))
INTERVAL = int(os.getenv("INTERVAL"))
DATA_FILE = str(os.getenv("DATA_FILE"))
AD_THRESHOLD = int(os.getenv("AD_THRESHOLD"))

tls = tools(json_address=DATA_FILE)

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

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        keyboard = [
            ['/add', '/delete'],
            ['/my_ads']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "به ربات دیوار خوش آمدید! ",
            reply_markup=reply_markup
        )
    
    except Exception as e:
        logger.error(f"Error in start handler function: {e}")
        return

# Add command
async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        await update.message.reply_text("""عملیات افزودن آگهی را شروع شده است.
برای لغو عملیات افزودن آگهی، /cancel را ارسال کنید.
                                        
                                        لطفاً عنوان آگهی را وارد کنید:""")
        return TITLE
    
    except Exception as e:
        logger.error(f"Error in add_start function: {e}")
        return ConversationHandler.END

async def add_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['title'] = update.message.text.strip()
        await update.message.reply_text("لینک آرشیو را وارد کنید:")
        return LINK_PAGE
    
    except Exception as e:
        logger.error(f"Error in add_title function: {e}")
        return ConversationHandler.END

async def add_link_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['link_page'] = update.message.text.strip()
        await update.message.reply_text("لینک صفحه آگهی را وارد کنید:")
        return LINK_AD
    
    except Exception as e:
        logger.error(f"Error in add_link_page function: {e}")
        return ConversationHandler.END

async def add_link_ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        context.user_data['link_ad'] = update.message.text.strip()

        title = context.user_data['title']
        link_page = context.user_data['link_page']
        link_ad = context.user_data['link_ad']

        res = tls.add(link_page=link_page, link_ad=link_ad, title=title, user_id=user_id)
        if res == True:
            await update.message.reply_text(f'آگهی "{title}" با موفقیت ذخیره شد.')
        else:
            await update.message.reply_text("عملیات افزودن با خطا مواجه شد !")
        return ConversationHandler.END
    
    except Exception as e:
        logger.error(f"Error in add_link_ad function: {e}")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("عملیات افزودن آگهی لغو شد.")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in cancel function: {e}")
        await update.message.reply_text("عملیات با خطا مواجه شد !")
        return ConversationHandler.END

# Delete command
async def handle_delete_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        data = tls.load_titles()
        titles = [i[2] for i in data.get(user_id, [])]
        if not titles:
            return await update.message.reply_text('عنوانی برای حذف وجود ندارد.')
        buttons = [[InlineKeyboardButton(t, callback_data=f'delete|{t}')] for t in titles]
        markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text('عنوان مورد نظر را برای حذف انتخاب کنید:', reply_markup=markup)
    
    except Exception as e:
        logger.error(f"Error in handle_delete_cmd function: {e}")
        return

# Show my ads command
async def handle_my_ads_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        res = tls.view_ads(user_id=user_id)
        if res == "NO_TITLE":
            await update.message.reply_text('آگهی وجود ندارد.')
            return
        elif res == False:
            await update.message.reply_text('عملیات ناموق بود . لطفا دوباره تلاش کنید')
            return
        
        await update.message.reply_text(res)
    
    except Exception as e:
        logger.error(f"Error in handle_delete_cmd function: {e}")
        return

# Callback handler
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        user_id = str(query.from_user.id)
        action, title = query.data.split('|', 1)

        if action == 'delete':
            res = tls.delete(title=title, user_id=user_id)
            if res == True:
                await query.edit_message_text('عنوان با موفقیت حذف شد.')
                return
            elif res == "UNKNOWN_TITLE":
                await query.edit_message_text('عنوان یافت نشد.')
                return
            else:
                await query.edit_message_text('مشکلی در حذف پیش آمد . لطفا دوباره تلاش کنید')
                return
        await update.message.reply_text('درخواست شما معتبر نیست !')
        return
            
    except Exception as e:
        logger.error(f"Error in handle_callback function: {e}")
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
       await update.message.reply_text('درخواست شما معتبر نیست !')
    
    except Exception as e:
        logger.error(f"Error in handle_message function: {e}")
        return


async def task(context: ContextTypes.DEFAULT_TYPE):
    try:
        data = tls.load_titles()
        for user_id, ads in data.items():
            for ad in ads:        
                link_page, link_ad, title, status = ad
                
                res = await scrape_data(link_page, link_ad, AD_THRESHOLD)
                        
                if res == False:
                    await context.bot.send_message(chat_id=user_id,text=f"""ERROR
در عملیات پیدا کردن آگهی \'{title}\' مشکلی پیش آمده""")

                elif res == "NOHTML":
                    await context.bot.send_message(chat_id=user_id,text=f"""ERROR
در عملیات پیدا کردن آگهی \'{title}\' مشکلی پیش آمده

error  : آدرس صفحه  {link_page} مشکل دارد""")
                
                elif res == "NOTIN_THRESHOLD":
                    await context.bot.send_message(chat_id=user_id, text=f"""آگهی  \'{title}\' شما در {AD_THRESHOLD} تا آگهی اول صفحه آرشیو نیست""")
                
                # the res is index of ad     
                else:
                    ads[ads.index(ad)] = [link_page, link_ad, title, res]
                    data[user_id] = ads
                    tls.save_titles(data)
                    if status != res:
                        w = "بالا" if status > res else "پایین"
                        await context.bot.send_message(chat_id=user_id, text=f"""آگهی \'{title}\' در 5 آگهی اول سایت قرار دارد
اما آگهی شما نسبت به گدشته {w} تر رفته

لینک آگهی
{link_ad}

لینک آرشیو 
{link_page}""")
                    
                    
                    else:
                        await context.bot.send_message(chat_id=user_id, text=f"""آگهی \'{title}\' در 5 آگهی اول سایت قرار دارد
رتبه:  {res}

لینک آگهی
{link_ad}

لینک آرشیو 
{link_page}""")
        
        
            
    except Exception as e:
        logger.error(f"Error in task function: {e}")


def main():
    try:
        application = ApplicationBuilder().token(BOT_TOKEN).build()

        # set handlers
        application.add_handler(CommandHandler('start', start))
        
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('add', add_start)],
            states={
                TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_title)],
                LINK_PAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_link_page)],
                LINK_AD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_link_ad)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        application.add_handler(conv_handler)
        application.add_handler(CommandHandler('delete', handle_delete_cmd))
        application.add_handler(CommandHandler('my_ads', handle_my_ads_cmd))
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        
        # run tls every hour
        application.job_queue.run_repeating(task, interval=INTERVAL, first=0)

        
        # run bot
        application.run_webhook(
            listen='127.0.0.1',
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f'https://diwar.loca.lt/{BOT_TOKEN}',
        )
    
    except Exception as e:
        logger.error(f"Error in main function: {e}")

if __name__ == '__main__':
    logger.info("Bot is starting...")
    main()
