import os
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")
CHANNEL_ID = -1003870890884

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

(NAME, CITY, ADDRESS, SERVICE,
 CLEANING_TYPE, CLEANING_AREA,
 COMBO_KITCHEN_AREA, COMBO_BATHROOM_AREA, COMBO_ROOM_AREA,
 CHIMCH_WHAT, CHIMCH_SOFA_SIZE, CHIMCH_MATTRESS_SIZE,
 DATE, PHONE, CONFIRM) = range(15)

CITIES = ["Київ", "Харків", "Одеса", "Дніпро", "Біла Церква", "Львів"]
SERVICES = ["🧹 Прибирання", "🛋 Хімчистка"]
CLEANING_TYPES = [
    "🧹 Генеральне — від 4 000 грн",
    "🫧 Підтримуюче — від 2 250 грн",
    "📅 Планувальне — від 2 000 грн/тиж",
    "🔀 Комбіноване"
]
CLEANING_AREAS_GEN = [
    "40-60 м² — від 4 000 грн",
    "70-90 м² — від 6 000 грн",
    "100-140 м² — від 8 400 грн"
]
CLEANING_AREAS_PID = [
    "40-60 м² — від 2 250 грн",
    "70-90 м² — від 4 000 грн",
    "100-140 м² — від 3 000 грн"
]
CLEANING_AREAS_PLAN = [
    "40-60 м² — від 2 000 грн/тиж",
    "70-90 м² — від 2 800 грн/тиж",
    "100-140 м² — від 4 800 грн/тиж"
]
KITCHEN_AREAS = [
    "до 6 м² — від 1 800 грн",
    "до 10 м² — від 2 400 грн",
    "до 20 м² — від 3 100 грн"
]
BATHROOM_AREAS = [
    "до 5 м² — від 1 300 грн",
    "до 10 м² — від 1 800 грн",
    "до 20 м² — від 2 600 грн"
]
ROOM_AREAS_GEN = [
    "40-60 м² — від 4 000 грн",
    "70-90 м² — від 6 000 грн",
    "100-140 м² — від 8 400 грн"
]
CHIMCH_ITEMS = [
    "🛋 Диван",
    "🛏 Матрас",
    "💺 Крісло — від 400 грн",
    "🪑 Стілець — від 200 грн",
    "🚗 Автосидіння — 550 грн/місце",
    "🟫 Килим — від 160 грн/м²"
]
SOFA_SIZES = [
    "2-місний — від 1 100 грн",
    "3-місний — від 1 650 грн",
    "4-місний — від 2 200 грн",
    "Кутовий — від 2 400 грн",
    "Великий модульний — від 2 700 грн"
]
MATTRESS_SIZES = [
    "Дитячий — від 300 грн",
    "Односпальний — від 550 грн",
    "Полуторний — від 800 грн",
    "Двоспальний — від 1 100 грн"
]

SYSTEM_PROMPT = """Ти — дружелюбний менеджер сервісу прибирання та хімчистки. 
Відповідай коротко, по справі, українською мовою.
Якщо клієнт питає про ціни:
- Генеральне прибирання: від 4000 грн (40-60м²), від 6000 грн (70-90м²), від 8400 грн (100-140м²)
- Підтримуюче: від 2250 грн (40-60м²), від 4000 грн (70-90м²), від 3000 грн (100-140м²)
- Хімчистка дивану: від 1100 грн (2-місний) до 2700 грн (великий модульний)
- Хімчистка матраса: від 300 грн (дитячий) до 1100 грн (двоспальний)
Якщо клієнт хоче замовити — скажи йому написати /start"""

def kb(options, back=None):
    keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in options]
    if back:
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data=f"back_{back}")])
    return InlineKeyboardMarkup(keyboard)

def get_cleaning_areas(cleaning_type):
    if "Генеральне" in cleaning_type:
        return CLEANING_AREAS_GEN
    elif "Підтримуюче" in cleaning_type:
        return CLEANING_AREAS_PID
    elif "Планувальне" in cleaning_type:
        return CLEANING_AREAS_PLAN
    return CLEANING_AREAS_GEN

async def send_to_channel(context, summary):
    try:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"🔔 *НОВА ЗАЯВКА!*\n\n{summary}",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Помилка відправки в канал: {e}")

async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}]
        )
        await update.message.reply_text(response.content[0].text)
    except Exception:
        await update.message.reply_text("Вибачте, сталася помилка. Спробуйте ще раз або напишіть /start")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 Вітаємо у сервісі професійного прибирання та хімчистки! 🧹✨\n\n"
        "Ми працюємо у Києві, Харкові, Одесі, Дніпрі, Білій Церкві та Львові.\n\n"
        "Як вас звати?"
    )
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
    await query.edit_message_text(
        f"📍 Чудово! {query.data}.\n\n"
        f"Вкажіть адресу де потрібне прибирання\n(вулиця, будинок, квартира):"
    )
    return ADDRESS

async def address_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    await update.message.reply_text(
        "Оберіть що вас цікавить:",
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
        await query.edit_message_text("Оберіть що вас цікавить:", reply_markup=kb(SERVICES, back="city"))
        return SERVICE
    context.user_data["cleaning_type"] = query.data
    if "Комбіноване" in query.data:
        await query.edit_message_text(
            "🔀 Комбіноване прибирання\n\n"
            "🍳 Оберіть площу *кухні*:",
            parse_mode="Markdown",
            reply_markup=kb(KITCHEN_AREAS, back="cleaning_type")
        )
        return COMBO_KITCHEN_AREA
    else:
        areas = get_cleaning_areas(query.data)
        await query.edit_message_text(
            "📐 Оберіть площу приміщення:",
            reply_markup=kb(areas, back="cleaning_type")
        )
        return CLEANING_AREA

async def cleaning_area_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_cleaning_type":
        await query.edit_message_text("🧹 Оберіть тип прибирання:", reply_markup=kb(CLEANING_TYPES, back="service"))
        return CLEANING_TYPE
    context.user_data["area"] = query.data
    price = query.data.split("—")[1].strip() if "—" in query.data else ""
    context.user_data["price"] = price
    await query.edit_message_text(
        f"✅ {context.user_data['cleaning_type'].split('—')[0].strip()}\n"
        f"📐 {query.data.split('—')[0].strip()}\n"
        f"💰 Вартість: *{price}*\n\n"
        f"📅 На яку дату вам зручно?\n"
        f"Напишіть, наприклад: *субота 10:00* або *26 квітня після 14:00*",
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
    await query.edit_message_text(
        f"🍳 Кухня: *{query.data}* ✅\n\n"
        f"🚿 Оберіть площу *ванної кімнати*:",
        parse_mode="Markdown",
        reply_markup=kb(BATHROOM_AREAS, back="combo_kitchen")
    )
    return COMBO_BATHROOM_AREA

async def combo_bathroom_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_combo_kitchen":
        await query.edit_message_text(
            "🍳 Оберіть площу *кухні*:",
            parse_mode="Markdown",
            reply_markup=kb(KITCHEN_AREAS, back="cleaning_type")
        )
        return COMBO_KITCHEN_AREA
    context.user_data["bathroom_area"] = query.data
    await query.edit_message_text(
        f"🍳 Кухня: *{context.user_data['kitchen_area']}* ✅\n"
        f"🚿 Ванна: *{query.data}* ✅\n\n"
        f"🛏 Оберіть площу *кімнат*:",
        parse_mode="Markdown",
        reply_markup=kb(ROOM_AREAS_GEN, back="combo_bathroom")
    )
    return COMBO_ROOM_AREA

async def combo_room_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_combo_bathroom":
        await query.edit_message_text(
            f"🍳 Кухня: *{context.user_data['kitchen_area']}* ✅\n\n"
            f"🚿 Оберіть площу *ванної кімнати*:",
            parse_mode="Markdown",
            reply_markup=kb(BATHROOM_AREAS, back="combo_kitchen")
        )
        return COMBO_BATHROOM_AREA
    context.user_data["room_area"] = query.data
    k = context.user_data['kitchen_area']
    b = context.user_data['bathroom_area']
    r = query.data
    await query.edit_message_text(
        f"✅ Комбіноване прибирання:\n"
        f"🍳 Кухня: *{k}*\n"
        f"🚿 Ванна: *{b}*\n"
        f"🛏 Кімнати: *{r}*\n\n"
        f"📅 На яку дату вам зручно?\n"
        f"Напишіть, наприклад: *субота 10:00* або *26 квітня після 14:00*",
        parse_mode="Markdown"
    )
    return DATE

async def chimch_what_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_service":
        await query.edit_message_text("Оберіть що вас цікавить:", reply_markup=kb(SERVICES, back="city"))
        return SERVICE
    context.user_data["chimch_item"] = query.data
    if "Диван" in query.data:
        await query.edit_message_text(
            "🛋 Оберіть розмір дивану:",
            reply_markup=kb(SOFA_SIZES, back="chimch")
        )
        return CHIMCH_SOFA_SIZE
    elif "Матрас" in query.data:
        await query.edit_message_text(
            "🛏 Оберіть розмір матраса:",
            reply_markup=kb(MATTRESS_SIZES, back="chimch")
        )
        return CHIMCH_MATTRESS_SIZE
    else:
        price = query.data.split("—")[1].strip() if "—" in query.data else "уточнюється"
        context.user_data["chimch_price"] = price
        await query.edit_message_text(
            f"💰 *{query.data}*\n\n"
            f"📅 На яку дату вам зручно?\n"
            f"Напишіть, наприклад: *субота 10:00* або *26 квітня після 14:00*",
            parse_mode="Markdown"
        )
        return DATE

async def chimch_sofa_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_chimch":
        await query.edit_message_text("🛋 Що потрібно почистити?", reply_markup=kb(CHIMCH_ITEMS, back="service"))
        return CHIMCH_WHAT
    context.user_data["chimch_size"] = query.data
    context.user_data["chimch_price"] = query.data.split("—")[1].strip() if "—" in query.data else ""
    await query.edit_message_text(
        f"🛋 Диван *{query.data}* ✅\n\n"
        f"📅 На яку дату вам зручно?\n"
        f"Напишіть, наприклад: *субота 10:00* або *26 квітня після 14:00*",
        parse_mode="Markdown"
    )
    return DATE

async def chimch_mattress_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_chimch":
        await query.edit_message_text("🛋 Що потрібно почистити?", reply_markup=kb(CHIMCH_ITEMS, back="service"))
        return CHIMCH_WHAT
    context.user_data["chimch_size"] = query.data
    context.user_data["chimch_price"] = query.data.split("—")[1].strip() if "—" in query.data else ""
    await query.edit_message_text(
        f"🛏 Матрас *{query.data}* ✅\n\n"
        f"📅 На яку дату вам зручно?\n"
        f"Напишіть, наприклад: *субота 10:00* або *26 квітня після 14:00*",
        parse_mode="Markdown"
    )
    return DATE

async def date_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["date"] = update.message.text
    await update.message.reply_text(
        "📞 Вкажіть ваш номер телефону щоб менеджер міг підтвердити запис:"
    )
    return PHONE

async def phone_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    data = context.user_data
    service = data.get("service", "")

    if "Прибирання" in service:
        cleaning_type = data.get("cleaning_type", "")
        if "Комбіноване" in cleaning_type:
            service_text = (
                f"🔀 Комбіноване прибирання:\n"
                f"  🍳 Кухня: {data.get('kitchen_area')}\n"
                f"  🚿 Ванна: {data.get('bathroom_area')}\n"
                f"  🛏 Кімнати: {data.get('room_area')}"
            )
        else:
            service_text = (
                f"{cleaning_type.split('—')[0].strip()}\n"
                f"  📐 {data.get('area', '').split('—')[0].strip()}\n"
                f"  💰 {data.get('price')}"
            )
    else:
        item = data.get("chimch_item", "")
        size = data.get("chimch_size", "")
        price = data.get("chimch_price", "")
        service_text = f"🛋 Хімчистка: {item}\n  📏 {size}\n  💰 {price}"

    summary = (
        f"👤 Ім'я: {data.get('name')}\n"
        f"📍 Місто: {data.get('city')}\n"
        f"🏠 Адреса: {data.get('address')}\n"
        f"{service_text}\n"
        f"📅 Бажана дата: {data.get('date')}\n"
        f"📞 Телефон: {data.get('phone')}"
    )
    context.user_data["summary"] = summary

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
        await query.message.reply_text(
            "👋 Вітаємо у сервісі професійного прибирання та хімчистки! 🧹✨\n\n"
            "Ми працюємо у Києві, Харкові, Одесі, Дніпрі, Білій Церкві та Львові.\n\n"
            "Як вас звати?"
        )
        return NAME
    name = context.user_data.get("name", "")
    phone = context.user_data.get("phone", "")
    summary = context.user_data.get("summary", "")
    await send_to_channel(context, summary)
    await query.edit_message_text(
        f"🎉 {name}, дякуємо за замовлення!\n\n"
        f"Наш менеджер зателефонує вам на номер {phone} та підтвердить зручний час. ⏰\n\n"
        f"Якщо виникнуть питання — ми завжди на зв'язку! 😊"
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
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))
app.run_polling()
