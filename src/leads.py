import os
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

NAME, CITY, ADDRESS, SERVICE, CLEANING_TYPE, COMBO_ROOMS, AREA, CHIMCHISTKA_DETAIL, DATE, PHONE, CONFIRM = range(11)

CITIES = ["Київ", "Харків", "Одеса", "Дніпро", "Біла Церква", "Львів"]
SERVICES = ["🧹 Прибирання", "🛋 Хімчистка"]
CLEANING_TYPES = ["Генеральне", "Підтримуюче", "Комбіноване"]
CHIMCHISTKA_ITEMS = ["Диван", "Матрас", "Стільці/Крісла", "Автосидіння"]
AREAS = ["до 30 м²", "30-50 м²", "50-80 м²", "80-120 м²", "120+ м²"]
ROOMS = ["Кухня", "Кімната", "Ванна"]
ROOM_TYPES = ["Генеральне", "Підтримуюче"]

def make_keyboard(options, cols=2):
    buttons = [InlineKeyboardButton(opt, callback_data=opt) for opt in options]
    keyboard = [buttons[i:i+cols] for i in range(0, len(buttons), cols)]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("👋 Вітаємо! Як вас звати?")
    return NAME

async def name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        f"Приємно познайомитись, {update.message.text}! 😊\n\nОберіть ваше місто:",
        reply_markup=make_keyboard(CITIES)
    )
    return CITY

async def city_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["city"] = query.data
    await query.edit_message_text(
        f"📍 Місто: {query.data}\n\nВкажіть вашу адресу (вулиця, будинок, квартира):"
    )
    return ADDRESS

async def address_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    await update.message.reply_text(
        f"📍 Адреса збережена!\n\nОберіть тип послуги:",
        reply_markup=make_keyboard(SERVICES)
    )
    return SERVICE

async def service_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["service"] = query.data
    if "Прибирання" in query.data:
        await query.edit_message_text(
            f"🧹 Оберіть тип прибирання:",
            reply_markup=make_keyboard(CLEANING_TYPES)
        )
        return CLEANING_TYPE
    else:
        await query.edit_message_text(
            f"🛋 Що потрібно почистити?",
            reply_markup=make_keyboard(CHIMCHISTKA_ITEMS)
        )
        return CHIMCHISTKA_DETAIL

async def cleaning_type_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["cleaning_type"] = query.data
    if query.data == "Комбіноване":
        context.user_data["combo_rooms"] = {}
        context.user_data["rooms_to_process"] = list(ROOMS)
        room = context.user_data["rooms_to_process"].pop(0)
        context.user_data["current_room"] = room
        await query.edit_message_text(
            f"🏠 Комбіноване прибирання\n\nДля кімнати **{room}** оберіть тип прибирання:",
            parse_mode="Markdown",
            reply_markup=make_keyboard(ROOM_TYPES)
        )
        return COMBO_ROOMS
    else:
        await query.edit_message_text(
            f"📐 Оберіть площу приміщення:",
            reply_markup=make_keyboard(AREAS)
        )
        return AREA

async def combo_room_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    room = context.user_data["current_room"]
    context.user_data["combo_rooms"][room] = query.data
    if context.user_data["rooms_to_process"]:
        next_room = context.user_data["rooms_to_process"].pop(0)
        context.user_data["current_room"] = next_room
        await query.edit_message_text(
            f"🏠 Комбіноване прибирання\n\nДля **{next_room}** оберіть тип прибирання:",
            parse_mode="Markdown",
            reply_markup=make_keyboard(ROOM_TYPES)
        )
        return COMBO_ROOMS
    else:
        await query.edit_message_text(
            f"📐 Оберіть площу приміщення:",
            reply_markup=make_keyboard(AREAS)
        )
        return AREA

async def chimchistka_detail_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["detail"] = query.data
    await query.edit_message_text(
        f"📅 На яку дату та час вам зручно?\n\nНапишіть, наприклад: *завтра о 10:00* або *субота вранці*",
        parse_mode="Markdown"
    )
    return DATE

async def area_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["area"] = query.data
    await query.edit_message_text(
        f"📅 На яку дату та час вам зручно?\n\nНапишіть, наприклад: *завтра о 10:00* або *субота вранці*",
        parse_mode="Markdown"
    )
    return DATE

async def date_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["date"] = update.message.text
    await update.message.reply_text("📞 Вкажіть ваш номер телефону:")
    return PHONE

async def phone_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    data = context.user_data
    if "Прибирання" in data.get("service", ""):
        if data.get("cleaning_type") == "Комбіноване":
            rooms_text = "\n".join([f"  • {r}: {t}" for r, t in data.get("combo_rooms", {}).items()])
            service_text = f"🧹 Комбіноване прибирання:\n{rooms_text}"
        else:
            service_text = f"🧹 {data.get('cleaning_type')} прибирання\n📐 Площа: {data.get('area')}"
    else:
        service_text = f"🛋 Хімчистка: {data.get('detail')}"

    summary = (
        f"👤 Ім'я: {data.get('name')}\n"
        f"📍 Місто: {data.get('city')}\n"
        f"🏠 Адреса: {data.get('address')}\n"
        f"{service_text}\n"
        f"📅 Дата: {data.get('date')}\n"
        f"📞 Телефон: {data.get('phone')}"
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
        context.user_data.clear()
        await query.edit_message_text("🔄 Починаємо заново...")
        await query.message.reply_text("👋 Як вас звати?")
        return NAME
    await query.edit_message_text(
        "✅ Дякуємо! Ваше замовлення прийнято.\n\n"
        "Наш менеджер зв'яжеться з вами найближчим часом для підтвердження. 🙌"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скасовано. Напишіть /start щоб почати заново.")
    return ConversationHandler.END

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_received)],
        CITY: [CallbackQueryHandler(city_chosen)],
        ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_received)],
        SERVICE: [CallbackQueryHandler(service_chosen)],
        CLEANING_TYPE: [CallbackQueryHandler(cleaning_type_chosen)],
        COMBO_ROOMS: [CallbackQueryHandler(combo_room_chosen)],
        AREA: [CallbackQueryHandler(area_chosen)],
        CHIMCHISTKA_DETAIL: [CallbackQueryHandler(chimchistka_detail_chosen)],
        DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_received)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_received)],
        CONFIRM: [CallbackQueryHandler(confirm)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)
app.run_polling()
