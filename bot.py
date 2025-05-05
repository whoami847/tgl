import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegraph import Telegraph
from config import TELEGRAM_TOKEN

# Telegra.ph ক্লায়েন্ট
telegraph = Telegraph()

# /start কমান্ড
def start(update, context):
    update.message.reply_text(
        "আমি @vTelegraphBot! নিচের কাজ করতে পারি:\n"
        "- ছবি পাঠান (ডকুমেন্ট হিসেবে), আমি Telegra.ph-এ আপলোড করে লিঙ্ক দেব।\n"
        "- টেক্সট পাঠান, আমি Telegra.ph পেজ তৈরি করে লিঙ্ক দেব।\n"
        "- /sct TITLE কমান্ড ব্যবহার করে পরবর্তী পেজের টাইটেল সেট করুন।"
    )

# /sct কমান্ড (কাস্টম টাইটেল সেট করা)
def set_custom_title(update, context):
    if not context.args:
        update.message.reply_text("দয়া করে একটি টাইটেল দিন। উদাহরণ: /sct My Page")
        return
    title = " ".join(context.args)
    context.user_data["custom_title"] = title
    update.message.reply_text(f"পরবর্তী পেজের টাইটেল সেট করা হয়েছে: {title}")

# টেক্সট মেসেজ হ্যান্ডল করা
def handle_text(update, context):
    text = update.message.text
    title = context.user_data.get("custom_title", "Untitled")
    
    try:
        response = telegraph.create_page(
            title=title,
            html_content=f"<p>{text}</p>",
            return_content=True
        )
        update.message.reply_text(f"আপনার Telegra.ph পেজ: {response['url']}")
        # কাস্টম টাইটেল রিসেট
        context.user_data.pop("custom_title", None)
    except Exception as e:
        update.message.reply_text(f"পেজ তৈরিতে সমস্যা: {str(e)}")

# ছবি (ডকুমেন্ট হিসেবে) হ্যান্ডল করা
def handle_image(update, context):
    file = update.message.document
    if not file.mime_type.startswith('image/'):
        update.message.reply_text("দয়া করে একটি ছবি পাঠান (ডকুমেন্ট হিসেবে)।")
        return
    
    # ফাইল ডাউনলোড
    file_path = context.bot.get_file(file.file_id).download()
    try:
        # Telegra.ph-এ আপলোড
        result = telegraph.upload_file(file_path)
        link = f"https://telegra.ph{result[0]['src']}"
        update.message.reply_text(f"আপনার ছবির লিঙ্ক: {link}")
    except Exception as e:
        update.message.reply_text(f"আপলোডে সমস্যা: {str(e)}")
    finally:
        # ফাইল মুছে ফেলা
        if os.path.exists(file_path):
            os.remove(file_path)

# মেইন ফাংশন
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # কমান্ড হ্যান্ডলার
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("sct", set_custom_title))
    # মেসেজ হ্যান্ডলার
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dp.add_handler(MessageHandler(Filters.document, handle_image))

    # বট শুরু
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
