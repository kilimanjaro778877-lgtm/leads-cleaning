import os
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

CITY, SERVICE, CLEANING_TYPE, CLEANING_DETAIL, AREA, DATE, CONFIRM = range(7)

CITIES = ["Київ", "Харків", "Одеса", "Дніпро", "Біла Церква", "Львів"]
SERVICES = ["🧹 Прибирання", "🛋 Хімчистка"]
CLEANING_TYPES = ["Генеральне", "Підтримуюче", "Комбіноване"]
ХИМЧИСТКА_ITEMS = ["Диван", "Матрас", "Стільці/Крісла", "Автосидіння"]
AREAS = ["до 30 м²", "30-50 м²", "50-80 м²", "80-120 м²", "120+ м²"]

def make_keyboard(options, cols=2):
    buttons = [InlineKeyboardButton(opt, callback_data=opt) for opt in options]
    keyboard = [buttons[i:i+cols] for i in range(0, len(buttons), cols)]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 Вітаємо! Це сервіс замовлення прибирання та хімчистки.\n\nОберіть ваше місто:",
        reply_markup=make_keyboard(CITIES)
    )
    return CITY

async def city_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["city"] = query.data
    await query.edit_message_text(
        f"📍 Місто: {query.data}\n\nОберіть тип послуги:",
        reply_markup=make_keyboard(SERVICES)
    )
    return SERVICE

async def service_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["service"] = query.data
    if "Прибирання" in query.data:
        await query.edit_message_text(
            f"📍 Місто: {context.user_data['city']}\n🧹 Послуга: Прибирання\n\nОберіть тип прибирання:",
            reply_markup=make_keyboard(CLEANING_TYPES)
        )
        return CLEANING_TYPE
    else:
        await query.edit_message_text(
            f"📍 Місто: {context.user_data['city']}\n🛋 Послуга: Хімчистка\n\nЩо потрібно почистити?",
            reply_markup=make_keyboard(ХИМЧИСТКА_ITEMS)
        )
        return CLEANING_DETAIL

async def cleaning_type_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["cleaning_type"] = query.data
    await query.edit_message_text(
        f"📍 {context.user_data['city']} | 🧹 {query.data} прибирання\n\nОберіть площу приміщення:",
        reply_markup=make_keyboard(AREAS)
    )
    return AREA

async def cleaning_detail_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["detail"] = query.data
    await query.edit_message_text(
        f"📍 {context.user_data['city']} | 🛋 Хімчистка: {query.data}\n\nНа яку дату та час вам зручно?\n\nНапишіть, наприклад: *завтра о 10:00* або *субота вранці*",
        parse_mode="Markdown"
    )
    return DATE

async def area_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["area"] = query.data
    await query.edit_message_text(
        f"📍 {context.user_data['city']} | 🧹 {context.user_data['cleaning_type']} | 📐 {query.data}\n\nНа яку дату та час вам зручно?\n\nНапишіть, наприклад: *завтра о 10:00* або *субота вранці*",
        parse_mode="Markdown"
    )
    return DATE

async def date_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["date"] = update.message.text
    data = context.user_data
    service = data.get("service", "")
    if "Прибирання" in service:
        summary = (
            f"📍 Місто: {data.get('city')}\n"
            f"🧹 Тип: {data.get('cleaning_type')} прибирання\n"
            f"📐 Площа: {data.get('area')}\n"
            f"📅 Дата: {data.get('date')}"
        )
    else:
        summary = (
            f"📍 Місто: {data.get('city')}\n"
            f"🛋 Хімчистка: {data.get('detail')}\n"
            f"📅 Дата: {data.get('date')}"
        )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Підтвердити", callback_data="confirm")],
        [InlineKeyboardButton("🔄 Почати заново", callback_data="restart")]
    ])
    await update.message.reply_text(
        f"📋 Ваше замовлення:\n\n{summary}\n\nВсе вірно?",
        reply_markup=keyboard
    )
    return CONFIRM

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "restart":
        await query.edit_message_text("🔄 Починаємо заново...")
        await query.message.reply_text(
            "Оберіть ваше місто:",
            reply_markup=make_keyboard(CITIES)
        )
        context.user_data.clear()
        return CITY
    data = context.user_data
    await query.edit_message_text(
        "✅ Дякуємо! Ваше замовлення прийнято.\n\n"
        "Наш менеджер зв'яжеться з вами найближчим часом для підтвердження часу. 🙌"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скасовано. Напишіть /start щоб почати заново.")
    return ConversationHandler.END

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CITY: [CallbackQueryHandler(city_chosen)],
        SERVICE: [CallbackQueryHandler(service_chosen)],
        CLEANING_TYPE: [CallbackQueryHandler(cleaning_type_chosen)],
        CLEANING_DETAIL: [CallbackQueryHandler(cleaning_detail_chosen)],
        AREA: [CallbackQueryHandler(area_chosen)],
        DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_received)],
        CONFIRM: [CallbackQueryHandler(confirm)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)
app.run_polling()
