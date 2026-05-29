import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===================== SOZLAMALAR =====================
BOT_TOKEN = "8268089103:AAEtGGjLlCyyPbARmwulPFvhPeGm4JGc9LI"
CHANNEL_INVITE_LINK = "https://t.me/+y5rTJnsHY3ZkMjhi"
CHANNEL_ID = "@your_channel_username"  # <-- MUHIM: quyida o'qing

# ======================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def check_subscription(bot, user_id: int) -> bool:
    """Foydalanuvchi kanalga obuna bo'lganini tekshiradi."""
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in [
            ChatMember.MEMBER,
            ChatMember.ADMINISTRATOR,
            ChatMember.OWNER,
        ]
    except Exception as e:
        logger.error(f"Obuna tekshirishda xato: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi /start yozganda ishga tushadi."""
    user = update.effective_user
    is_subscribed = await check_subscription(context.bot, user.id)

    if is_subscribed:
        await send_welcome_content(update, user)
    else:
        keyboard = [
            [InlineKeyboardButton("📢 Kanalga obuna bo'lish", url=CHANNEL_INVITE_LINK)],
            [InlineKeyboardButton("✅ Obuna bo'ldim, tekshir!", callback_data="check_sub")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"👋 Salom, {user.first_name}!\n\n"
            "🔒 Kanalimizning barcha postlari, medialar va kontentlari "
            "faqat obunachilarga ko'rinadi.\n\n"
            "📢 Iltimos, postlarni ko'rish uchun kanalimizga obuna bo'ling!\n\n"
            "⬇️ Obuna bo'lgach, '✅ Obuna bo'ldim' tugmasini bosing.",
            reply_markup=reply_markup,
        )


async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi 'Obuna bo'ldim' tugmasini bosganda tekshiradi."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    is_subscribed = await check_subscription(context.bot, user.id)

    if is_subscribed:
        await query.message.delete()
        await send_welcome_content(update, user, via_callback=True)
    else:
        keyboard = [
            [InlineKeyboardButton("📢 Kanalga obuna bo'lish", url=CHANNEL_INVITE_LINK)],
            [InlineKeyboardButton("✅ Obuna bo'ldim, tekshir!", callback_data="check_sub")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"❌ {user.first_name}, siz hali kanalga obuna bo'lmagansiz!\n\n"
            "📢 Iltimos avval kanalga obuna bo'ling, so'ng qayta tekshiring.",
            reply_markup=reply_markup,
        )


async def send_welcome_content(update: Update, user, via_callback=False):
    """Obuna bo'lgan foydalanuvchiga kontent yuboradi."""
    message_text = (
        f"✅ Rahmat, {user.first_name}! Siz kanalga obuna bo'lgansiz.\n\n"
        "🎉 Endi kanalimizning barcha postlari, medialar va kontentlari "
        "sizga ochiq!\n\n"
        "👉 Kanalga o'tish uchun: " + CHANNEL_INVITE_LINK
    )

    if via_callback:
        await update.callback_query.message.reply_text(message_text)
    else:
        await update.message.reply_text(message_text)


def main():
    """Botni ishga tushiradi."""
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_sub$"))

    logger.info("Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
