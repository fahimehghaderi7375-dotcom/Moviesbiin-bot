import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
STORAGE_CHANNEL = os.getenv("STORAGE_CHANNEL")  # مثال: @moviesbiin_storage
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL")  # مثال: @moviesbiin

bot = telebot.TeleBot(BOT_TOKEN)


def is_member(user_id):
    try:
        member = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


def join_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            "📢 عضویت در کانال",
            url=f"https://t.me/{REQUIRED_CHANNEL.lstrip('@')}"
        )
    )
    keyboard.add(
        InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_join")
    )
    return keyboard


@bot.message_handler(commands=["start"])
def start(message):
    parts = message.text.split(maxsplit=1)

    if len(parts) > 1:
        payload = parts[1]

        if not is_member(message.from_user.id):
            bot.send_message(
                message.chat.id,
                "برای دریافت فایل ابتدا در کانال عضو شو 👇",
                reply_markup=join_keyboard()
            )
            return

        try:
            channel_id, msg_id = payload.split("_")
            bot.copy_message(
                message.chat.id,
                int(channel_id),
                int(msg_id)
            )
            return
        except Exception:
            pass

    bot.send_message(
        message.chat.id,
        "🎬 به ربات MoviesBiin خوش اومدی!\n\n"
        "برای دریافت فایل، لینک مخصوص فایل رو باز کن."
    )


@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "📚 راهنمای ربات\n\n"
        "برای دریافت فیلم یا سریال، لینک فایل موردنظر رو باز کن.\n"
        "در صورت نیاز ابتدا باید عضو کانال MoviesBiin باشی."
    )


@bot.message_handler(content_types=[
    "document", "video", "audio", "photo"
])
def receive_file(message):
    if not is_member(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "برای استفاده از ربات ابتدا در کانال عضو شو 👇",
            reply_markup=join_keyboard()
        )
        return

    try:
        copied = bot.copy_message(
            STORAGE_CHANNEL,
            message.chat.id,
            message.message_id
        )

        payload = f"{STORAGE_CHANNEL}_{copied.message_id}"
        bot_username = bot.get_me().username

        link = f"https://t.me/{bot_username}?start={payload}"

        bot.send_message(
            message.chat.id,
            f"✅ فایل ذخیره شد.\n\n"
            f"🔗 لینک دریافت فایل:\n{link}"
        )

    except Exception as e:
        bot.send_message(
            message.chat.id,
            "❌ مشکلی در ذخیره فایل پیش آمد."
        )
        print(e)


@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    if is_member(call.from_user.id):
        bot.answer_callback_query(
            call.id,
            "✅ عضویت شما تأیید شد."
        )
        bot.send_message(
            call.message.chat.id,
            "✅ عضویت تأیید شد. حالا لینک فایل رو باز کن."
        )
    else:
        bot.answer_callback_query(
            call.id,
            "❌ هنوز عضو کانال نیستید.",
            show_alert=True
        )


print("MoviesBiin bot is running...")
bot.infinity_polling(skip_pending=True)
