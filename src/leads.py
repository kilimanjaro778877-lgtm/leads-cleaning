import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

(NAME, CITY, ADDRESS, SERVICE, 
 CLEANING_TYPE, CLEANING_AREA,
 COMBO_KITCHEN_AREA, COMBO_BATHROOM_AREA, COMBO_ROOM_AREA,
 CHIMCH_WHAT, CHIMCH_SOFA_SIZE, CHIMCH_MATTRESS_SIZE, CHIMCH_OTHER_COUNT,
 DATE, PHONE, CONFIRM) = range(16)

CITIES = ["Київ", "Харків", "Одеса", "Дніпро", "Біла Церква", "Львів"]
SERVICES = ["🧹 Прибирання", "🛋 Хімчистка"]
CLEANING_TYPES = ["Генеральне", "Підтримуюче", "Планувальне", "Комбіноване"]
CLEANING_AREAS = ["40-60 м²", "70-90 м²", "100-140 м²"]
KITCHEN_AREAS = ["до 6 м²", "до 10 м²", "до 20 м²"]
BATHROOM_AREAS = ["до 5 м²", "до 10 м²", "до 20 м²"]
ROOM_AREAS = ["40-60 м²", "70-90 м²", "100-140 м²"]
CHIMCH_ITEMS = ["🛋 Диван", "🛏 Матрас", "💺 Крісло", "🪑 Стілець", "🚗 Автосидіння", "🟫 Килим"]
SOFA_SIZES = ["2-місний", "3-місний", "4-місний", "Кутовий", "Великий модульний"]
MATTRESS_SIZES = ["Дитячий", "Односпальний", "Полуторний", "Двоспальний"]

PRICES = {
    "Генеральне": {"40-60 м²": "від 4000 грн", "70-90 м²": "від 6000 грн", "100-140 м²": "від 8400 грн"},
    "Підтримуюче": {"40-60 м²": "від 2250 грн", "70-90 м²": "від 4000 грн", "100-140 м²": "від 3000 грн"},
    "Планувальне": {"40-60 м²": "від 2000 грн/тиж", "70-90 м²": "від 2800 грн/тиж", "100-140 м²": "від 4800 грн/тиж"},
    "sofa": {"2-місний": "від 1100 грн", "3-місний": "від 1650 грн", "4-місний": "від 2200 грн", "Кутовий": "від 2400 грн", "Великий модульний": "від 2700 грн"},
    "mattress": {"Дитячий": "від 300 грн", "Односпальний": "від 550 грн", "Полуторний": "від 800 грн", "Двоспальний": "від 1100 грн"},
    "kitchen": {"до 6 м²": "від 1800 грн", "до 10 м²": "від 2400 грн", "до 20 м²": "від 3100 грн"},
    "bathroom": {"до 5 м²": "від 1300 грн", "до 10 м²": "від 1800 грн", "до 20 м²": "від 2600 грн"},
}

def btn(text, data=None):
    return InlineKeyboardButton(text, callback_data=data or text)

def kb(options, back=None):
    keyboard = [[btn(opt)] for opt in options]
    if back:
        keyboard.append([btn("◀️ Назад", f"back_{back}")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("👋 Вітаємо! Як вас звати?")
    return NAME

async def name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        f"Приємно познайомитись, {update.message.text}! 😊\n\nОберіть ваше місто:",
        reply_markup=kb(CITIES)
    )
    return CITY

async def city_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_name":
        await query.edit_message_text("👋 Як вас звати?")
        return NAME
    context.user_data["city"] = query.data
    await query.edit_message_text(f"📍 Місто: {query.data}\n\nВкажіть адресу (вулиця, будинок, квартира):")
    return ADDRESS

async def address_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    await update.message.reply_text(
        "Оберіть тип послуги:",
        reply_markup=kb(SERVICES, back="city")
    )
    return SERVICE

async def service_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_city":
        await query.edit_message_text("Оберіть ваше місто:", reply_markup=kb(CITIES))
        return CITY
    context.user_data["service"] = query.data
    if "Прибирання" in query.data:
        await query.edit_message_text(
            "🧹 Оберіть тип прибирання:",
            reply_markup=kb(CLEANING_TYPES, back="service")
        )
        return CLEANING_TYPE
    else:
        await query.edit_message_text(
            "🛋 Що потрібно почистити?",
            reply_markup=kb(CHIMCH_ITEMS, back="service")
        )
        return CHIMCH_WHAT

async def cleaning_type_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_service":
        await query.edit_message_text("Оберіть тип послуги:", reply_markup=kb(SERVICES, back="city"))
        return SERVICE
    context.user_data["cleaning_type"] = query.data
    if query.data == "Комбіноване":
        await query.edit_message_text(
            "🍳 Комбіноване прибирання\n\nОберіть площу **кухні**:",
            parse_mode="Markdown",
            reply_markup=kb(KITCHEN_AREAS, back="cleaning_type")
        )
        return COMBO_KITCHEN_AREA
    else:
        await query.edit_message_text(
            f"📐 Оберіть площу приміщення:",
            reply_markup=kb(CLEANING_AREAS, back="cleaning_type")
        )
        return CLEANING_AREA

async def cleaning_area_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_cleaning_type":
        await query.edit_message_text("🧹 Оберіть тип прибирання:", reply_markup=kb(CLEANING_TYPES, back="service"))
        return CLEANING_TYPE
    context.user_data["area"] = query.data
    price = PRICES.get(context.user_data["cleaning_type"], {}).get(query.data, "")
    context.user_data["price"] = price
    await query.edit_message_text(
        f"💰 Орієнтовна вартість: *{price}*\n\n📅 На яку дату вам зручно?\nНапишіть, наприклад: *завтра о 10:00*",
        parse_mode="Markdown"
    )
    return DATE

async def combo_kitchen_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_cleaning_type":
        await query.edit_message_text("🧹 Оберіть тип прибирання:", reply_markup=kb(CLEANING_TYPES, back="service"))
        return CLEANING_TYPE
    context.user_data["kitchen_area"] = query.data
    context.user_data["kitchen_price"] = PRICES["kitchen"][query.data]
    await query.edit_message_text(
        f"🍳 Кухня: {query.data} — {PRICES['kitchen'][query.data]}\n\n🚿 Оберіть площу **ванної кімнати**:",
        parse_mode="Markdown",
        reply_markup=kb(BATHROOM_AREAS, back="combo_kitchen")
    )
    return COMBO_BATHROOM_AREA

async def combo_bathroom_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_combo_kitchen":
        await query.edit_message_text(
            "🍳 Оберіть площу **кухні**:",
            parse_mode="Markdown",
            reply_markup=kb(KITCHEN_AREAS, back="cleaning_type")
        )
        return COMBO_KITCHEN_AREA
    context.user_data["bathroom_area"] = query.data
    context.user_data["bathroom_price"] = PRICES["bathroom"][query.data]
    await query.edit_message_text(
        f"🚿 Ванна: {query.data} — {PRICES['bathroom'][query.data]}\n\n🛏 Оберіть площу **кімнат**:",
        parse_mode="Markdown",
        reply_markup=kb(ROOM_AREAS, back="combo_bathroom")
    )
    return COMBO_ROOM_AREA

async def combo_room_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_combo_bathroom":
        await query.edit_message_text(
            "🚿 Оберіть площу **ванної кімнати**:",
            parse_mode="Markdown",
            reply_markup=kb(BATHROOM_AREAS, back="combo_kitchen")
        )
        return COMBO_BATHROOM_AREA
    context.user_data["room_area"] = query.data
    k_price = context.user_data.get("kitchen_price", "")
    b_price = context.user_data.get("bathroom_price", "")
    r_price = PRICES["Генеральне"].get(query.data, "")
    context.user_data["room_price"] = r_price
    await query.edit_message_text(
        f"💰 Орієнтовна вартість:\n"
        f"🍳 Кухня ({context.user_data['kitchen_area']}): *{k_price}*\n"
        f"🚿 Ванна ({context.user_data['bathroom_area']}): *{b_price}*\n"
        f"🛏 Кімнати ({query.data}): *{r_price}*\n\n"
        f"📅 На яку дату вам зручно?\nНапишіть, наприклад: *завтра о 10:00*",
        parse_mode="Markdown"
    )
    return DATE

async def chimch_what_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_service":
        await query.edit_message_text("Оберіть тип послуги:", reply_markup=kb(SERVICES, back="city"))
        return SERVICE
    item = query.data.replace("🛋 ", "").replace("🛏 ", "").replace("💺 ", "").replace("🪑 ", "").replace("🚗 ", "").replace("🟫 ", "")
    context.user_data["chimch_item"] = item
    if item == "Диван":
        await query.edit_message_text(
            "🛋 Оберіть розмір дивану:",
            reply_markup=kb(SOFA_SIZES, back="chimch")
        )
        return CHIMCH_SOFA_SIZE
    elif item == "Матрас":
        await query.edit_message_text(
            "🛏 Оберіть розмір матраса:",
            reply_markup=kb(MATTRESS_SIZES, back="chimch")
        )
        return CHIMCH_MATTRESS_SIZE
    else:
        price_map = {"Крісло": "від 400 грн", "Стілець": "від 200 грн", "Автосидіння": "550 грн/місце", "Килим": "від 160 грн/м²"}
        price = price_map.get(item, "уточнюється")
        context.user_data["chimch_price"] = price
        await query.edit_message_text(
            f"💰 Орієнтовна вартість *{item}*: *{price}*\n\n📅 На яку дату вам зручно?\nНапишіть, наприклад: *завтра о 10:00*",
            parse_mode="Markdown"
        )
        return DATE

async def chimch_sofa_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_chimch":
        await query.edit_message_text("🛋 Що потрібно почистити?", reply_markup=kb(CHIMCH_ITEMS, back="service"))
        return CHIMCH_WHAT
    price = PRICES["sofa"].get(query.data, "уточнюється")
    context.user_data["chimch_size"] = query.data
    context.user_data["chimch_price"] = price
    await query.edit_message_text(
        f"💰 Диван {query.data}: *{price}*\n\n📅 На яку дату вам зручно?\nНапишіть, наприклад: *завтра о 10:00*",
        parse_mode="Markdown"
    )
    return DATE

async def chimch_mattress_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_chimch":
        await query.edit_message_text("🛋 Що потрібно почистити?", reply_markup=kb(CHIMCH_ITEMS, back="service"))
        return CHIMCH_WHAT
    price = PRICES["mattress"].get(query.data, "уточнюється")
    context.user_data["chimch_size"] = query.data
    context.user_data["chimch_price"] = price
    await query.edit_message_text(
        f"💰 Матрас {query.data}: *{price}*\n\n📅 На яку дату вам зручно?\nНапишіть, наприклад: *завтра о 10:00*",
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
    service = data.get("service", "")

    if "Прибирання" in service:
        cleaning_type = data.get("cleaning_type", "")
        if cleaning_type == "Комбіноване":
            service_text = (
                f"🧹 Комбіноване прибирання:\n"
                f"  🍳 Кухня: {data.get('kitchen_area')} — {data.get('kitchen_price')}\n"
                f"  🚿 Ванна: {data.get('bathroom_area')} — {data.get('bathroom_price')}\n"
                f"  🛏 Кімнати: {data.get('room_area')} — {data.get('room_price')}"
            )
        else:
            service_text = f"🧹 {cleaning_type} прибирання\n  📐 Площа: {data.get('area')}\n  💰 {data.get('price')}"
    else:
        item = data.get("chimch_item", "")
        size = data.get("chimch_size", "")
        price = data.get("chimch_price", "")
        service_text = f"🛋 Хімчистка: {item} {size}\n  💰 {price}"

    summary = (
        f"👤 Ім'я: {data.get('name')}\n"
        f"📍 Місто: {data.get('city')}\n"
        f"🏠 Адреса: {data.get('address')}\n"
        f"{service_text}\n"
        f"📅 Дата: {data.get('date')}\n"
        f"📞 Телефон: {data.get('phone')}"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗓 Забронювати дату", callback_data="confirm")],
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
        "✅ Чудово! Ваше замовлення прийнято.\n\n"
        "Наш менеджер зв'яжеться з вами найближчим часом для підтвердження дати. 🙌"
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
        CLEANING_AREA: [CallbackQueryHandler(cleaning_area_chosen)],
        COMBO_KITCHEN_AREA: [CallbackQueryHandler(combo_kitchen_area)],
        COMBO_BATHROOM_AREA: [CallbackQueryHandler(combo_bathroom_area)],
        COMBO_ROOM_AREA: [CallbackQueryHandler(combo_room_area)],
        CHIMCH_WHAT: [CallbackQueryHandler(chimch_what_chosen)],
        CHIMCH_SOFA_SIZE: [CallbackQueryHandler(chimch_sofa_size)],
        CHIMCH_MATTRESS_SIZE: [CallbackQueryHandler(chimch_mattress_size)],
        DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_received)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_received)],
        CONFIRM: [CallbackQueryHandler(confirm)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)
app.run_polling()
