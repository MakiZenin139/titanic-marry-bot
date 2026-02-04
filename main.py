
# -*- coding: utf-8 -*-
# ==============================================================================
# 👑 TITANIC MARRY SYSTEM: THE SUPREME ETERNAL MONOLITH V10000 👑
# ------------------------------------------------------------------------------
# АВТОР ПРОЕКТА: Maki Zenin
# ССЫЛКА НА АВТОРА: https://t.me/MakiDV
# ВЕРСИЯ: 10000.0 (GIGA-LONG UNABRIDGED EDITION)
# СТРОК КОДА: 1000+ (ПОЛНЫЙ РАЗВОРОТ БЕЗ ЕДИНОГО СОКРАЩЕНИЯ)
# ------------------------------------------------------------------------------
# СТАТУС: АБСОЛЮТНАЯ ВЕРСИЯ.
# ==============================================================================

import asyncio
import logging
import json
import os
import html
import sys
import random
import time
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (
    InlineQueryResultArticle, 
    InputTextMessageContent, 
    InlineQuery, 
    CallbackQuery, 
    Message
)
from aiogram.client.session.aiohttp import AiohttpSession

# ==============================================================================
# [⚙️] ГЛОБАЛЬНАЯ КОНФИГУРАЦИЯ И КОНСТАНТЫ
# ==============================================================================
API_TOKEN = "8357705272:AAEEVtpuV-_JtB3If3yn82nhp3RlGM0Xwa8"
DATABASE_PATH = "titanic_giga_database.json"
AUTHOR_LABEL = "Maki Zenin"
AUTHOR_URL_LINK = "https://t.me/MakiDV"

# Константы игрового процесса
XP_REWARD_LOVE = 25   # Очки за комплимент
XP_REWARD_HIT = 0     # Сковорода без очков
LEVEL_CAP_MAX = 5     # Максимальный уровень
LEVEL_STEP_XP = 100   # Очков до нового уровня
COOLDOWN_LOVE = 3600  # Кулдаун комплимента 1 час (3600 секунд)

# Список наград за достижение уровней (расширенный)
REWARDS_TABLE = {
    1: "🛡",
    2: "🏆",
    3: "⚔️",
    4: "🧥",
    5: "🔱"
}

# Магазин подарков
SHOP_ITEMS = {
    "rose": {"name": "Роза", "price": 50, "emoji": "🌹"},
    "chocolate": {"name": "Шоколад", "price": 75, "emoji": "🍫"},
    "ring": {"name": "Кольцо", "price": 150, "emoji": "💍"},
    "teddy": {"name": "Плюшевый мишка", "price": 100, "emoji": "🧸"},
    "diamond": {"name": "Бриллиант", "price": 300, "emoji": "💎"},
    "crown": {"name": "Корона", "price": 500, "emoji": "👑"},
    "heart": {"name": "Золотое сердце", "price": 250, "emoji": "❤️"},
    "flower": {"name": "Букет цветов", "price": 120, "emoji": "🌸"}
}

# Настройка сессии и прокси
session_interface = AiohttpSession(proxy="http://proxy.server:3128")
bot_instance = Bot(token=API_TOKEN, session=session_interface)
dp_engine = Dispatcher()

# Глобальное логирование для отладки
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("TITANIC_SUPREME")

# ==============================================================================
# [📂] СИСТЕМА УПРАВЛЕНИЯ БАЗОЙ ДАННЫХ (DATABASE)
# ==============================================================================
def db_storage_init():
    """Проверка наличия файла базы данных при запуске."""
    if not os.path.exists(DATABASE_PATH):
        try:
            with open(DATABASE_PATH, "w", encoding="utf-8") as f:
                json.dump({}, f)
            logger.info("Системный файл базы данных успешно инициализирован.")
        except Exception as error:
            logger.error(f"Критическая ошибка инициализации базы: {error}")

def db_load_all_records():
    """Загрузка всех записей из JSON файла в оперативную память."""
    try:
        if os.path.exists(DATABASE_PATH):
            with open(DATABASE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as error:
        logger.error(f"Ошибка при чтении базы данных: {error}")
        return {}

def db_save_all_records(data_map):
    """Синхронизация данных из памяти в физический файл JSON."""
    try:
        with open(DATABASE_PATH, "w", encoding="utf-8") as f:
            json.dump(data_map, f, ensure_ascii=False, indent=4)
    except Exception as error:
        logger.error(f"Ошибка при сохранении базы данных: {error}")

# Кэширование базы данных в глобальную переменную
master_cache = db_load_all_records()

def get_or_create_user(user_id, first_name=""):
    """
    Получение объекта пользователя. 
    Если пользователя нет — создается полная структура данных на 15+ полей.
    """
    uid_str = str(user_id)
    clean_name = html.escape(first_name) if first_name else "Незнакомец"
    
    if uid_str not in master_cache:
        master_cache[uid_str] = {
            "name": clean_name,
            "gender": None, 
            "theme": "Обычная",
            "partner_id": None,
            "love_points": 0,
            "level": 1,
            "last_action_timestamp": 0,
            "last_love_timestamp": 0,
            "marriage_date": None,
            "marriage_ts": 0,
            "marriage_gift": None,
            "inventory": [],
            "gifts_received": [],
            "children_list": [],
            "parents": {"father": None, "mother": None},
            "privacy": False,
            "status": "Свободен",
            "reg_date": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        }
        db_save_all_records(master_cache)
    else:
        # Обновление имени, если оно изменилось в Telegram
        if first_name and master_cache[uid_str]["name"] != clean_name:
            master_cache[uid_str]["name"] = clean_name
            db_save_all_records(master_cache)
        # Добавление новых полей для старых пользователей
        if "last_love_timestamp" not in master_cache[uid_str]:
            master_cache[uid_str]["last_love_timestamp"] = 0
        if "gifts_received" not in master_cache[uid_str]:
            master_cache[uid_str]["gifts_received"] = []
        if "parents" not in master_cache[uid_str]:
            master_cache[uid_str]["parents"] = {"father": None, "mother": None}
        if "privacy" not in master_cache[uid_str]:
            master_cache[uid_str]["privacy"] = False
            db_save_all_records(master_cache)
            
    return master_cache[uid_str]

def get_user_mention_link(user_id):
    """Формирование безопасной HTML-ссылки на профиль пользователя."""
    user_data = master_cache.get(str(user_id))
    if not user_data:
        return f'<a href="tg://user?id={user_id}">Участник</a>'
    return f'<a href="tg://user?id={user_id}">{user_data["name"]}</a>'

def get_gender_text(gender, text_type):
    """
    Получение правильного склонения слов в зависимости от пола.
    text_type: 'partner', 'partner_gen', 'self_action', 'child', 'role'
    """
    if text_type == 'partner':
        # Для обозначения партнера (именительный падеж)
        return "Супруга" if gender == "М" else "Супруг"
    elif text_type == 'partner_gen':
        # Для обозначения партнера (родительный падеж - вашей супруги/вашего супруга)
        return "вашей Супруги" if gender == "М" else "вашего Супруга"
    elif text_type == 'self_action':
        # Для глаголов (подарил/подарила)
        return "" if gender == "М" else "а"
    elif text_type == 'child':
        # Для детей (сын/дочь)
        return "сын" if gender == "М" else "дочь"
    elif text_type == 'role':
        # Для ролей (Лорд/Леди)
        return "Лорд" if gender == "М" else "Леди"
    elif text_type == 'role_lower':
        # Для ролей в нижнем регистре (лорд/леди)
        return "лорд" if gender == "М" else "леди"
    elif text_type == 'partner_role':
        # Для роли партнера
        return "Леди" if gender == "М" else "Лорд"
    elif text_type == 'partner_role_lower':
        # Для роли партнера в нижнем регистре
        return "леди" if gender == "М" else "лорд"
    return ""

def calculate_marriage_age(start_timestamp):
    """Детальный расчет времени со дня свадьбы."""
    if not start_timestamp or start_timestamp == 0:
        return "0 дней"
    
    current_ts = int(time.time())
    delta = current_ts - start_timestamp
    
    days = delta // 86400
    hours = (delta % 86400) // 3600
    minutes = (delta % 3600) // 60
    
    return f"{days}д. {hours}ч. {minutes}м."

def format_cooldown_time(seconds):
    """Форматирование оставшегося времени кулдауна."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}ч. {minutes}м."
    elif minutes > 0:
        return f"{minutes}м. {secs}с."
    else:
        return f"{secs}с."

def get_top_couples_by_time():
    """Получение топ-5 пар по длительности брака."""
    couples = []
    processed = set()
    
    for uid, user in master_cache.items():
        if user["partner_id"] and uid not in processed and str(user["partner_id"]) not in processed:
            partner = master_cache.get(str(user["partner_id"]))
            if partner:
                marriage_duration = int(time.time()) - user["marriage_ts"]
                couples.append({
                    "user1_id": int(uid),
                    "user2_id": user["partner_id"],
                    "user1_name": user["name"],
                    "user2_name": partner["name"],
                    "duration": marriage_duration,
                    "marriage_date": user["marriage_date"]
                })
                processed.add(uid)
                processed.add(str(user["partner_id"]))
    
    couples.sort(key=lambda x: x["duration"], reverse=True)
    return couples[:5]

def get_top_couples_by_points():
    """Получение топ-5 пар по общему количеству очков."""
    couples = []
    processed = set()
    
    for uid, user in master_cache.items():
        if user["partner_id"] and uid not in processed and str(user["partner_id"]) not in processed:
            partner = master_cache.get(str(user["partner_id"]))
            if partner:
                total_points = user["love_points"] + partner["love_points"]
                couples.append({
                    "user1_id": int(uid),
                    "user2_id": user["partner_id"],
                    "user1_name": user["name"],
                    "user2_name": partner["name"],
                    "total_points": total_points,
                    "user1_points": user["love_points"],
                    "user2_points": partner["love_points"]
                })
                processed.add(uid)
                processed.add(str(user["partner_id"]))
    
    couples.sort(key=lambda x: x["total_points"], reverse=True)
    return couples[:5]

# ==============================================================================
# [🆙] СИСТЕМА ПРОГРЕССИИ И УРОВНЕЙ
# ==============================================================================
def check_and_apply_level_up(user_record):
    """Проверка условий для повышения уровня и выдача наград."""
    current_xp = user_record["love_points"]
    old_level = user_record["level"]
    
    # Расчет уровня: каждые 100 очков +1 уровень
    new_level = (current_xp // LEVEL_STEP_XP) + 1
    
    # Лимит уровней
    if new_level > LEVEL_CAP_MAX:
        new_level = LEVEL_CAP_MAX
        
    if new_level > old_level:
        user_record["level"] = new_level
        # Добавление награды в подарки
        reward_item = REWARDS_TABLE.get(new_level)
        if reward_item and reward_item not in user_record["gifts_received"]:
            user_record["gifts_received"].append(reward_item)
        return True
    return False

# ==============================================================================
# [🎨] КОНСТРУКТОРЫ ИНТЕРФЕЙСА (UI BUILDER)
# ==============================================================================
def build_main_menu():
    """Создание клавиатуры главного меню."""
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="👤 Мой Профиль", callback_data="btn_profile_home"))
    kb.row(types.InlineKeyboardButton(text="⚙️ Настройки", callback_data="btn_settings_list"),
           types.InlineKeyboardButton(text="🎁 Магазин", callback_data="btn_shop_main"))
    kb.row(types.InlineKeyboardButton(text="📜 Справочник", callback_data="btn_help_info"),
           types.InlineKeyboardButton(text="🏆 Топ Пар", callback_data="btn_top_couples"))
    kb.row(types.InlineKeyboardButton(text="💔 Развестись", callback_data="btn_divorce_init"))
    return kb.as_markup()

def build_back_button():
    """Кнопка возврата в меню."""
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🔙 Вернуться в меню", callback_data="btn_nav_main"))
    return kb.as_markup()

def build_shop_menu(user_points):
    """Создание клавиатуры магазина с ценами."""
    kb = InlineKeyboardBuilder()
    
    # Разбиваем товары по 2 в ряд с ценами
    items = list(SHOP_ITEMS.items())
    for i in range(0, len(items), 2):
        row_buttons = []
        for j in range(2):
            if i + j < len(items):
                item_id, item_data = items[i + j]
                # Проверяем, хватает ли очков
                can_afford = user_points >= item_data['price']
                button_text = f"{item_data['emoji']} {item_data['name']} - {item_data['price']}⭐"
                row_buttons.append(
                    types.InlineKeyboardButton(
                        text=button_text,
                        callback_data=f"shop_view_{item_id}"
                    )
                )
        kb.row(*row_buttons)
    
    kb.row(types.InlineKeyboardButton(text="🔙 Назад в меню", callback_data="btn_nav_main"))
    return kb.as_markup()

# ==============================================================================
# [🚀] ОБРАБОТЧИКИ КОМАНД (HANDLERS)
# ==============================================================================
@dp_engine.message(CommandStart())
async def cmd_start_handler(message: Message):
    """Обработка команды /start."""
    user = get_or_create_user(message.from_user.id, message.from_user.first_name)
    
    header = (
        f"👑 <b>TITANIC MARRY SYSTEM</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Разработчик: <a href='{AUTHOR_URL_LINK}'>{AUTHOR_LABEL}</a>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )

    if user["gender"] is None:
        kb = InlineKeyboardBuilder()
        kb.row(types.InlineKeyboardButton(text="Мужчина 🧔", callback_data="act_set_sex_m"),
               types.InlineKeyboardButton(text="Женщина 👩", callback_data="act_set_sex_f"))
        await message.answer(
            f"{header}Добро пожаловать в систему! Для начала выберите ваш пол:",
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            f"{header}Рады видеть вас снова, {user['name']}!\nЧем займемся сегодня?",
            reply_markup=build_main_menu(),
            parse_mode="HTML"
        )

@dp_engine.callback_query(F.data.startswith("act_set_sex_"))
async def callback_gender_setup(callback: CallbackQuery):
    """Сохранение выбранного пола."""
    u = get_or_create_user(callback.from_user.id)
    u["gender"] = "М" if "sex_m" in callback.data else "Ж"
    db_save_all_records(master_cache)
    await callback.message.edit_text(
        "✅ Пол успешно установлен. Ваш профиль готов к работе!",
        reply_markup=build_main_menu()
    )

# ==============================================================================
# [👤] МОДУЛЬ ОТОБРАЖЕНИЯ ПРОФИЛЯ
# ==============================================================================
@dp_engine.callback_query(F.data.startswith("btn_profile_home"))
async def callback_profile_render(callback: CallbackQuery):
    """Генерация и отображение детального профиля."""
    # Определение ID цели (свой или чужой)
    data = callback.data.split(":")
    uid = int(data[1]) if len(data) > 1 else callback.from_user.id
    
    u = get_or_create_user(uid)
    
    # Проверка приватности профиля
    if uid != callback.from_user.id and u.get("privacy", False):
        await callback.answer("🔒 Этот профиль скрыт настройками приватности!", show_alert=True)
        return
    
    is_medieval = (u["theme"] == "Средневековая")
    
    # СТАТИСТИКА БРАКА
    if u["partner_id"]:
        partner_mention = get_user_mention_link(u["partner_id"])
        partner_data = master_cache.get(str(u["partner_id"]))
        partner_label = get_gender_text(u["gender"], 'partner')
        marry_age = calculate_marriage_age(u["marriage_ts"])
        partner_status = "✅"
    else:
        partner_mention = "❌"
        partner_label = get_gender_text(u["gender"], 'partner')
        marry_age = "—"
        partner_status = "❌"

    # СПИСОК ДЕТЕЙ
    label_kids = "Наследники" if is_medieval else "Дети"
    if u["children_list"]:
        child_links = [get_user_mention_link(c_id) for c_id in u["children_list"]]
        children_str = ", ".join(child_links)
        children_status = "✅"
    else:
        children_str = "❌"
        children_status = "❌"
    
    # РОДИТЕЛИ
    parents_info = u.get("parents", {"father": None, "mother": None})
    if parents_info["father"]:
        father_str = get_user_mention_link(parents_info["father"])
        father_status = "✅"
    else:
        father_str = "❌"
        father_status = "❌"
        
    if parents_info["mother"]:
        mother_str = get_user_mention_link(parents_info["mother"])
        mother_status = "✅"
    else:
        mother_str = "❌"
        mother_status = "❌"
    
    # ПОДАРКИ
    gifts_str = " ".join(u["gifts_received"]) if u["gifts_received"] else "❌"

    # СБОРКА ТЕКСТА ШАБЛОНА
    if is_medieval:
        role = get_gender_text(u["gender"], 'role')
        text = (
            f"🏰 <b>ВЕЛИКИЙ КОРОЛЕВСКИЙ ПРОФИЛЬ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>{role}:</b> {u['name']}\n"
            f"🛡 <b>Уровень Чести:</b> {u['level']}/5\n"
            f"💠 <b>Очки Славы:</b> {u['love_points']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💍 <b>В союзе с:</b> {partner_mention}\n"
            f"⏳ <b>Длительность:</b> {marry_age}\n"
            f"👶 <b>{label_kids}:</b> {children_str}\n"
            f"👨 <b>Отец:</b> {father_str}\n"
            f"👩 <b>Мать:</b> {mother_str}\n"
            f"📅 <b>Дата Указа:</b> {u['marriage_date'] or '—'}\n"
            f"🎁 <b>Дар:</b> {u['marriage_gift'] or '—'}\n"
            f"💝 <b>Подарки:</b> {gifts_str}\n"
        )
    else:
        text = (
            f"👤 <b>ЛИЧНЫЙ ПРОФИЛЬ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 <b>Имя:</b> {u['name']}\n"
            f"🆙 <b>Уровень:</b> {u['level']}/5\n"
            f"💖 <b>Любовь:</b> {u['love_points']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"❤️ <b>{partner_label}:</b> {partner_mention}\n"
            f"⏱ <b>Стаж:</b> {marry_age}\n"
            f"🍼 <b>{label_kids}:</b> {children_str}\n"
            f"👨 <b>Отец:</b> {father_str}\n"
            f"👩 <b>Мать:</b> {mother_str}\n"
            f"📅 <b>Свадьба:</b> {u['marriage_date'] or '—'}\n"
            f"🎁 <b>Подарок:</b> {u['marriage_gift'] or '—'}\n"
            f"💝 <b>Подарки:</b> {gifts_str}\n"
        )

    text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🆔 <code>{uid}</code>"
    
    # КЛАВИАТУРА ПРОФИЛЯ
    kb = InlineKeyboardBuilder()
    if u["partner_id"]:
        kb.row(types.InlineKeyboardButton(text=f"➡️ Профиль {partner_label}а", callback_data=f"btn_profile_home:{u['partner_id']}"))
    if parents_info["father"]:
        kb.row(types.InlineKeyboardButton(text="👨 Профиль Отца", callback_data=f"btn_profile_home:{parents_info['father']}"))
    if parents_info["mother"]:
        kb.row(types.InlineKeyboardButton(text="👩 Профиль Матери", callback_data=f"btn_profile_home:{parents_info['mother']}"))
    kb.row(types.InlineKeyboardButton(text="🔙 Назад", callback_data="btn_nav_main"))
    
    # Попытка отправить фото профиля
    try:
        photos = await bot_instance.get_user_profile_photos(uid, limit=1)
        if photos.total_count > 0:
            await callback.message.delete()
            await bot_instance.send_photo(
                chat_id=callback.from_user.id,
                photo=photos.photos[0][-1].file_id,
                caption=text,
                reply_markup=kb.as_markup(),
                parse_mode="HTML"
            )
            return
    except:
        pass
        
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")

# ==============================================================================
# [🎁] МОДУЛЬ МАГАЗИНА
# ==============================================================================
@dp_engine.callback_query(F.data == "btn_shop_main")
async def shop_main_handler(callback: CallbackQuery):
    """Отображение главного меню магазина."""
    u = get_or_create_user(callback.from_user.id)
    is_medieval = (u["theme"] == "Средневековая")
    
    if not u["partner_id"]:
        await callback.answer("❌ Магазин доступен только для женатых пар!", show_alert=True)
        return
    
    partner_gen = get_gender_text(u["gender"], 'partner_gen')
    
    if is_medieval:
        role = get_gender_text(u["gender"], 'role_lower')
        text = (
            f"🏰 <b>КОРОЛЕВСКАЯ СОКРОВИЩНИЦА</b>\n\n"
            f"Добро пожаловать в палату даров, {role} {u['name']}!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💠 Ваши очки славы: <b>{u['love_points']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Выберите дар для {partner_gen}:\n"
        )
    else:
        text = (
            f"🎁 <b>МАГАЗИН ПОДАРКОВ</b>\n\n"
            f"Добро пожаловать, {u['name']}!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💖 Ваши очки: <b>{u['love_points']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Выберите подарок для {partner_gen}:\n"
        )
    
    await callback.message.edit_text(text, reply_markup=build_shop_menu(u['love_points']), parse_mode="HTML")

@dp_engine.callback_query(F.data.startswith("shop_view_"))
async def shop_view_handler(callback: CallbackQuery):
    """Просмотр подробностей товара."""
    item_id = callback.data.split("_")[2]
    
    if item_id not in SHOP_ITEMS:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return
    
    u = get_or_create_user(callback.from_user.id)
    item = SHOP_ITEMS[item_id]
    is_medieval = (u["theme"] == "Средневековая")
    
    if is_medieval:
        text = (
            f"🏰 <b>ОПИСАНИЕ ДАРА</b>\n\n"
            f"{item['emoji']} <b>{item['name']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💠 Стоимость: <b>{item['price']}</b> очков славы\n"
            f"💰 У вас: <b>{u['love_points']}</b> очков\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
    else:
        text = (
            f"🎁 <b>ПОДАРОК</b>\n\n"
            f"{item['emoji']} <b>{item['name']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💖 Цена: <b>{item['price']}</b> очков\n"
            f"💰 У вас: <b>{u['love_points']}</b> очков\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
    
    if u['love_points'] >= item['price']:
        text += "✅ У вас достаточно очков для покупки!"
    else:
        text += f"❌ Не хватает: <b>{item['price'] - u['love_points']}</b> очков"
    
    kb = InlineKeyboardBuilder()
    if u['love_points'] >= item['price']:
        kb.row(types.InlineKeyboardButton(text=f"✅ Купить за {item['price']} очков", callback_data=f"shop_buy_{item_id}"))
    kb.row(types.InlineKeyboardButton(text="🔙 К товарам", callback_data="btn_shop_main"))
    kb.row(types.InlineKeyboardButton(text="🏠 В меню", callback_data="btn_nav_main"))
    
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@dp_engine.callback_query(F.data.startswith("shop_buy_"))
async def shop_buy_handler(callback: CallbackQuery):
    """Покупка подарка."""
    item_id = callback.data.split("_")[2]
    
    if item_id not in SHOP_ITEMS:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return
    
    u = get_or_create_user(callback.from_user.id)
    
    if not u["partner_id"]:
        await callback.answer("❌ У вас нет супруга!", show_alert=True)
        return
    
    item = SHOP_ITEMS[item_id]
    
    if u["love_points"] < item["price"]:
        await callback.answer(f"❌ Недостаточно очков! Нужно: {item['price']}", show_alert=True)
        return
    
    # Списание очков
    u["love_points"] -= item["price"]
    
    # Добавление подарка партнеру
    partner = get_or_create_user(u["partner_id"])
    partner["gifts_received"].append(item["emoji"])
    
    db_save_all_records(master_cache)
    
    is_medieval = (u["theme"] == "Средневековая")
    action_suffix = get_gender_text(u["gender"], 'self_action')
    
    if is_medieval:
        role = get_gender_text(u["gender"], 'role')
        partner_role = get_gender_text(partner["gender"], 'role_lower')
        success_text = (
            f"✅ <b>ДАР ВРУЧЕН!</b>\n\n"
            f"{role} {u['name']} преподнес{action_suffix} {item['emoji']} {item['name']} "
            f"{partner_role} {partner['name']}!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💠 Потрачено очков славы: <b>{item['price']}</b>\n"
            f"💠 Осталось: <b>{u['love_points']}</b>"
        )
    else:
        success_text = (
            f"✅ <b>ПОДАРОК ВРУЧЕН!</b>\n\n"
            f"{u['name']} подарил{action_suffix} {item['emoji']} {item['name']} {partner['name']}!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💖 Потрачено очков: <b>{item['price']}</b>\n"
            f"💖 Осталось: <b>{u['love_points']}</b>"
        )
    
    # Уведомление партнеру
    try:
        partner_notify = (
            f"🎁 <b>ВАМ ПОДАРОК!</b>\n\n"
            f"Ваш супруг{get_gender_text(u['gender'], 'self_action')} {u['name']} подарил{action_suffix} вам {item['emoji']} {item['name']}!"
        )
        await bot_instance.send_message(u["partner_id"], partner_notify, parse_mode="HTML")
    except:
        pass
    
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🛍 Купить еще", callback_data="btn_shop_main"))
    kb.row(types.InlineKeyboardButton(text="🔙 В меню", callback_data="btn_nav_main"))
    
    await callback.message.edit_text(success_text, reply_markup=kb.as_markup(), parse_mode="HTML")

# ==============================================================================
# [🏆] МОДУЛЬ ТОПОВ ПАР
# ==============================================================================
@dp_engine.callback_query(F.data == "btn_top_couples")
async def top_couples_handler(callback: CallbackQuery):
    """Главное меню топов пар."""
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="⏳ Топ по времени", callback_data="top_time"))
    kb.row(types.InlineKeyboardButton(text="💖 Топ по очкам", callback_data="top_points"))
    kb.row(types.InlineKeyboardButton(text="🏠 Топ домов", callback_data="top_houses_dev"))
    kb.row(types.InlineKeyboardButton(text="🔙 Назад", callback_data="btn_nav_main"))
    
    text = (
        f"🏆 <b>РЕЙТИНГ ПАР</b>\n\n"
        f"Выберите категорию рейтинга:\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏳ <b>По времени</b> - самые долгие союзы\n"
        f"💖 <b>По очкам</b> - самые любящие пары\n"
        f"🏠 <b>По домам</b> - в разработке"
    )
    
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@dp_engine.callback_query(F.data == "top_time")
async def top_time_handler(callback: CallbackQuery):
    """Топ пар по времени."""
    top_couples = get_top_couples_by_time()
    
    if not top_couples:
        await callback.answer("❌ Нет данных о парах!", show_alert=True)
        return
    
    text = (
        f"🏆 <b>ТОП-5 ПАР ПО ДЛИТЕЛЬНОСТИ БРАКА</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    
    for idx, couple in enumerate(top_couples):
        days = couple["duration"] // 86400
        hours = (couple["duration"] % 86400) // 3600
        
        text += (
            f"{medals[idx]} <b>#{idx + 1}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 Пара: {get_user_mention_link(couple['user1_id'])} ❤️ {get_user_mention_link(couple['user2_id'])}\n"
            f"⏳ Вместе: <b>{days}</b> дн. <b>{hours}</b> ч.\n"
            f"📅 Дата брака: <b>{couple['marriage_date']}</b>\n\n"
        )
    
    kb = InlineKeyboardBuilder()
    
    # Добавляем кнопки для просмотра профилей топ-3
    if len(top_couples) > 0:
        kb.row(
            types.InlineKeyboardButton(text="🥇 Профиль 1-й пары", callback_data=f"top_profile:{top_couples[0]['user1_id']}:{top_couples[0]['user2_id']}")
        )
    if len(top_couples) > 1:
        kb.row(
            types.InlineKeyboardButton(text="🥈 Профиль 2-й пары", callback_data=f"top_profile:{top_couples[1]['user1_id']}:{top_couples[1]['user2_id']}")
        )
    if len(top_couples) > 2:
        kb.row(
            types.InlineKeyboardButton(text="🥉 Профиль 3-й пары", callback_data=f"top_profile:{top_couples[2]['user1_id']}:{top_couples[2]['user2_id']}")
        )
    
    kb.row(types.InlineKeyboardButton(text="🔙 К топам", callback_data="btn_top_couples"))
    kb.row(types.InlineKeyboardButton(text="🏠 В меню", callback_data="btn_nav_main"))
    
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@dp_engine.callback_query(F.data == "top_points")
async def top_points_handler(callback: CallbackQuery):
    """Топ пар по очкам."""
    top_couples = get_top_couples_by_points()
    
    if not top_couples:
        await callback.answer("❌ Нет данных о парах!", show_alert=True)
        return
    
    text = (
        f"🏆 <b>ТОП-5 ПАР ПО ОЧКАМ ЛЮБВИ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    
    for idx, couple in enumerate(top_couples):
        text += (
            f"{medals[idx]} <b>#{idx + 1}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 Пара: {get_user_mention_link(couple['user1_id'])} ❤️ {get_user_mention_link(couple['user2_id'])}\n"
            f"💖 Всего очков: <b>{couple['total_points']}</b>\n"
            f"├─ {couple['user1_name']}: <b>{couple['user1_points']}</b>\n"
            f"└─ {couple['user2_name']}: <b>{couple['user2_points']}</b>\n\n"
        )
    
    kb = InlineKeyboardBuilder()
    
    # Добавляем кнопки для просмотра профилей топ-3
    if len(top_couples) > 0:
        kb.row(
            types.InlineKeyboardButton(text="🥇 Профиль 1-й пары", callback_data=f"top_profile:{top_couples[0]['user1_id']}:{top_couples[0]['user2_id']}")
        )
    if len(top_couples) > 1:
        kb.row(
            types.InlineKeyboardButton(text="🥈 Профиль 2-й пары", callback_data=f"top_profile:{top_couples[1]['user1_id']}:{top_couples[1]['user2_id']}")
        )
    if len(top_couples) > 2:
        kb.row(
            types.InlineKeyboardButton(text="🥉 Профиль 3-й пары", callback_data=f"top_profile:{top_couples[2]['user1_id']}:{top_couples[2]['user2_id']}")
        )
    
    kb.row(types.InlineKeyboardButton(text="🔙 К топам", callback_data="btn_top_couples"))
    kb.row(types.InlineKeyboardButton(text="🏠 В меню", callback_data="btn_nav_main"))
    
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@dp_engine.callback_query(F.data.startswith("top_profile:"))
async def top_profile_handler(callback: CallbackQuery):
    """Меню выбора профиля из пары."""
    parts = callback.data.split(":")
    user1_id = int(parts[1])
    user2_id = int(parts[2])
    
    u1 = get_or_create_user(user1_id)
    u2 = get_or_create_user(user2_id)
    
    text = (
        f"👥 <b>ВЫБЕРИТЕ ПРОФИЛЬ</b>\n\n"
        f"Чей профиль вы хотите посмотреть?\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"1️⃣ {u1['name']}\n"
        f"2️⃣ {u2['name']}"
    )
    
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(text=f"1️⃣ {u1['name']}", callback_data=f"btn_profile_home:{user1_id}"),
        types.InlineKeyboardButton(text=f"2️⃣ {u2['name']}", callback_data=f"btn_profile_home:{user2_id}")
    )
    kb.row(types.InlineKeyboardButton(text="🔙 Назад к топам", callback_data="btn_top_couples"))
    
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@dp_engine.callback_query(F.data == "top_houses_dev")
async def top_houses_dev_handler(callback: CallbackQuery):
    """Заглушка для топа домов (в разработке)."""
    text = (
        f"🏠 <b>ТОП ДОМОВ</b>\n\n"
        f"⚠️ Данный раздел находится в разработке!\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Скоро здесь появится рейтинг семейных домов с уникальными характеристиками:\n\n"
        f"• 🏡 Уровень дома\n"
        f"• 💰 Богатство семьи\n"
        f"• 👨‍👩‍👧‍👦 Количество детей\n"
        f"• 🎁 Коллекция подарков\n"
        f"• ⭐ Престиж династии\n\n"
        f"Следите за обновлениями!"
    )
    
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🔙 К топам", callback_data="btn_top_couples"))
    kb.row(types.InlineKeyboardButton(text="🏠 В меню", callback_data="btn_nav_main"))
    
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")

# ==============================================================================
# [💍] ИНЛАЙН-РЕЖИМ (ГЛАВНАЯ ЛОГИКА)
# ==============================================================================
@dp_engine.inline_query()
async def inline_query_logic(query: InlineQuery):
    """Обработка инлайн-запросов: Брак, Комплименты, Сковорода."""
    u = get_or_create_user(query.from_user.id, query.from_user.first_name)
    if u["gender"] is None: return 
        
    results = []
    is_medieval = (u["theme"] == "Средневековая")

    # 1. ПРЕДЛОЖЕНИЕ БРАКА
    if not u["partner_id"]:
        m_title = "🏰 Издать Королевский указ" if is_medieval else "💍 Сделать предложение"
        
        # ОФОРМЛЕНИЕ ПРЕДЛОЖЕНИЯ
        if is_medieval:
            role = get_gender_text(u["gender"], 'role')
            partner_type = "достойную спутницу" if u["gender"] == "М" else "достойного спутника"
            m_text = (
                f"🏰 <b>КОРОЛЕВСКИЙ УКАЗ №{random.randint(100, 999)}</b>\n\n"
                f"Сим объявляется поиск священного союза!\n"
                f"{role} <b>{u['name']}</b> ищет {partner_type}.\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Да пребудет с вами сила!"
            )
        else:
            m_text = (
                f"💍 <b>ПРЕДЛОЖЕНИЕ РУКИ И СЕРДЦА</b>\n\n"
                f"<b>{u['name']}</b> предлагает создать союз!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Готовы ли вы принять это предложение?"
            )
            
        results.append(InlineQueryResultArticle(
            id="inline_marry",
            title=m_title,
            description="Отправить запрос на брак",
            input_message_content=InputTextMessageContent(message_text=m_text, parse_mode="HTML"),
            reply_markup=InlineKeyboardBuilder().row(
                types.InlineKeyboardButton(text="✅ Принять", callback_data=f"core_marry_ok_{query.from_user.id}"),
                types.InlineKeyboardButton(text="❌ Отклонить", callback_data=f"core_marry_no_{query.from_user.id}")
            ).as_markup()
        ))
    else:
        # ДЕЙСТВИЯ ДЛЯ ЖЕНАТЫХ
        partner = master_cache.get(str(u["partner_id"]), {})
        p_name = partner.get("name", "Партнер")
        
        # Проверка кулдауна комплимента
        current_time = int(time.time())
        time_since_love = current_time - u.get("last_love_timestamp", 0)
        can_give_love = time_since_love >= COOLDOWN_LOVE
        
        # 2. КОМПЛИМЕНТ (С КУЛДАУНОМ)
        if can_give_love:
            love_desc = f"Для: {p_name} | +25 XP | КД: 1 час"
        else:
            cooldown_left = COOLDOWN_LOVE - time_since_love
            love_desc = f"Для: {p_name} | КД: {format_cooldown_time(cooldown_left)}"
        
        if is_medieval:
            role = get_gender_text(u["gender"], 'role')
            partner_role = get_gender_text(partner.get("gender"), 'role_lower')
            action = "восхищен" if u["gender"] == "М" else "восхищена"
            love_text = (
                f"💝 <b>БЗЫНЬ!</b>\n\n"
                f"📜 <b>ГРАМОТА ВЕРНОСТИ</b>\n\n"
                f"{role} <b>{u['name']}</b> {action} благородством {partner_role} <b>{p_name}</b>!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Сие деяние укрепит союз двух сердец!"
            )
        else:
            love_text = (
                f"💝 <b>БЗЫНЬ!</b>\n\n"
                f"✨ <b>ПРИЗНАНИЕ В ЛЮБВИ</b>\n\n"
                f"<b>{u['name']}</b> дарит комплимент <b>{p_name}</b>!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Это укрепит вашу связь ❤️"
            )
        
        results.append(InlineQueryResultArticle(
            id="inline_love",
            title="❤️ Комплимент",
            description=love_desc,
            input_message_content=InputTextMessageContent(
                message_text=love_text,
                parse_mode="HTML"
            ),
            reply_markup=InlineKeyboardBuilder().row(
                types.InlineKeyboardButton(
                    text="❤️ Принять (+25 XP)" if can_give_love else f"⏳ Ожидание ({format_cooldown_time(COOLDOWN_LOVE - time_since_love)})",
                    callback_data=f"core_action_love_{query.from_user.id}_{u['partner_id']}" if can_give_love else "core_action_cooldown"
                )
            ).as_markup()
        ))

        # 3. СКОВОРОДА (БЕЗ КД, БЕЗ XP)
        if is_medieval:
            role = get_gender_text(u["gender"], 'role')
            partner_role = get_gender_text(partner.get("gender"), 'role_lower')
            action = "огрел" if u["gender"] == "М" else "огрела"
            hit_text = (
                f"🍳 <b>БЗЫНЬ!</b>\n\n"
                f"🔨 <b>КОРОЛЕВСКАЯ КАРА</b>\n\n"
                f"{role} <b>{u['name']}</b> {action} {partner_role} <b>{p_name}</b> сковородой по лбу!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Сие наказание да послужит уроком! ⚔️"
            )
        else:
            hit_text = (
                f"🍳 <b>БЗЫНЬ!</b>\n\n"
                f"💥 <b>СЕМЕЙНЫЙ СКАНДАЛ</b>\n\n"
                f"<b>{u['name']}</b> бьет сковородой <b>{p_name}</b>!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Вот это страсти! 😅"
            )
        
        results.append(InlineQueryResultArticle(
            id="inline_hit",
            title="🍳 Ударить сковородой",
            description=f"Для: {p_name} | Без XP | Без КД",
            input_message_content=InputTextMessageContent(
                message_text=hit_text,
                parse_mode="HTML"
            ),
            reply_markup=InlineKeyboardBuilder().row(
                types.InlineKeyboardButton(text="🤕 Получить", callback_data=f"core_action_hit_{query.from_user.id}_{u['partner_id']}")
            ).as_markup()
        ))

        # 4. УСЫНОВЛЕНИЕ
        if is_medieval:
            role = get_gender_text(u["gender"], 'role_lower')
            partner_role = get_gender_text(partner.get("gender"), 'role_lower')
            child_text = (
                f"👶 <b>УКАЗ О НАСЛЕДНИКЕ</b>\n\n"
                f"Королевская семья {role} <b>{u['name']}</b> и {partner_role} <b>{p_name}</b> ищет достойного наследника!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Станьте частью великого рода! 👑"
            )
        else:
            child_text = (
                f"🍼 <b>УСЫНОВЛЕНИЕ</b>\n\n"
                f"Семья <b>{u['name']}</b> и <b>{p_name}</b> хочет усыновить вас!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Станьте частью их счастливой семьи! 👨‍👩‍👧"
            )
        
        results.append(InlineQueryResultArticle(
            id="inline_child",
            title="👶 Усыновить",
            description="Предложить стать вашим ребенком",
            input_message_content=InputTextMessageContent(
                message_text=child_text,
                parse_mode="HTML"
            ),
            reply_markup=InlineKeyboardBuilder().row(
                types.InlineKeyboardButton(text="🐥 Стать ребенком", callback_data=f"core_child_add_{query.from_user.id}")
            ).as_markup()
        ))

    await query.answer(results, is_personal=True, cache_time=0)

# ==============================================================================
# [⚔️] КОРНЕВАЯ ЛОГИКА ДЕЙСТВИЙ
# ==============================================================================
@dp_engine.callback_query(F.data.startswith("core_action_"))
async def core_action_processor(callback: CallbackQuery):
    """Логика начисления XP за действия (комплимент/удар)."""
    data_parts = callback.data.split("_")
    
    # Проверка на кулдаун
    if data_parts[2] == "cooldown":
        await callback.answer("⏳ Нужно подождать перед следующим комплиментом!", show_alert=True)
        return
    
    action_type = data_parts[2]
    initiator_id = int(data_parts[3])
    target_partner_id = int(data_parts[4])
    
    u_init = get_or_create_user(initiator_id)
    
    # ЗАЩИТА: Проверка, что нажимает именно партнер инициатора
    if callback.from_user.id != target_partner_id:
        is_medieval = (u_init["theme"] == "Средневековая")
        if is_medieval:
            error_msg = (
                f"🚫 <b>ОТКАЗАНО В ДОСТУПЕ!</b>\n\n"
                f"Сие действие дозволено лишь законному супругу!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Вы не состоите в союзе с инициатором данного действия."
            )
        else:
            error_msg = (
                f"❌ <b>ЭТО НЕ ВАША ПАРА!</b>\n\n"
                f"Это действие предназначено только для супруга инициатора!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Вы не можете взаимодействовать с чужой парой."
            )
        await callback.answer(error_msg, show_alert=True)
        return
        
    u_acc = get_or_create_user(callback.from_user.id)
    is_medieval = (u_init["theme"] == "Средневековая")
    
    # Обработка действий
    if action_type == "love":
        # Проверка кулдауна для инициатора
        current_time = int(time.time())
        time_since_love = current_time - u_init.get("last_love_timestamp", 0)
        
        if time_since_love < COOLDOWN_LOVE:
            cooldown_left = COOLDOWN_LOVE - time_since_love
            if is_medieval:
                cd_msg = f"⏳ Деяние отвергнуто! Время до следующей грамоты: {format_cooldown_time(cooldown_left)}"
            else:
                cd_msg = f"⏳ Кулдаун! Осталось: {format_cooldown_time(cooldown_left)}"
            await callback.answer(cd_msg, show_alert=True)
            return
        
        # Начисление XP
        xp = XP_REWARD_LOVE
        u_init["love_points"] += xp
        u_acc["love_points"] += xp
        u_init["last_love_timestamp"] = current_time
        
        # Проверка уровней
        up1 = check_and_apply_level_up(u_init)
        up2 = check_and_apply_level_up(u_acc)
        
        db_save_all_records(master_cache)
        
        if is_medieval:
            msg = (
                f"💝 <b>БЗЫНЬ!</b>\n\n"
                f"❤️ <b>ГРАМОТА ПРИНЯТА!</b>\n\n"
                f"Оба супруга получили по <b>+{xp} очков славы</b>!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Да укрепится ваш священный союз!"
            )
        else:
            msg = (
                f"💝 <b>БЗЫНЬ!</b>\n\n"
                f"❤️ <b>КОМПЛИМЕНТ ПРИНЯТ!</b>\n\n"
                f"Вы оба получили по <b>+{xp} XP</b>!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Ваша связь становится крепче! 💕"
            )
        
        if up1 or up2:
            msg += "\n\n🎊 <b>УРОВЕНЬ ПОВЫШЕН!</b> Загляните в профиль за наградой."
            
    elif action_type == "hit":
        # Сковорода без XP
        db_save_all_records(master_cache)
        
        if is_medieval:
            role = get_gender_text(u_acc["gender"], 'role')
            action = "принял" if u_acc["gender"] == "М" else "приняла"
            msg = (
                f"🍳 <b>БЗЫНЬ!</b>\n\n"
                f"🔨 <b>НАКАЗАНИЕ ПОЛУЧЕНО!</b>\n\n"
                f"{role} <b>{u_acc['name']}</b> {action} справедливое возмездие!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Сие да послужит уроком на будущее! ⚔️"
            )
        else:
            action = "принял" if u_acc["gender"] == "М" else "приняла"
            msg = (
                f"🍳 <b>БЗЫНЬ!</b>\n\n"
                f"🤕 <b>УДАР ПОЛУЧЕН!</b>\n\n"
                f"<b>{u_acc['name']}</b> {action} удар сковородой!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Надеюсь, это был урок! 😅"
            )
    
    await bot_instance.edit_message_text(
        inline_message_id=callback.inline_message_id,
        text=msg,
        parse_mode="HTML"
    )

@dp_engine.callback_query(F.data.startswith("core_marry_ok_"))
async def core_marry_accept(callback: CallbackQuery):
    """Процесс заключения брака."""
    i_id = int(callback.data.split("_")[3])
    
    # Защита от саможенитьбы
    if callback.from_user.id == i_id:
        await callback.answer("❌ На себе нельзя жениться!", show_alert=True)
        return
        
    u1, u2 = get_or_create_user(i_id), get_or_create_user(callback.from_user.id, callback.from_user.first_name)
    
    if u1["partner_id"] or u2["partner_id"]:
        await callback.answer("❌ Кто-то уже состоит в браке!", show_alert=True)
        return

    if u2["gender"] is None:
        u2["gender"] = "Ж" if u1["gender"] == "М" else "М"
    
    if u1["gender"] == u2["gender"]:
        await callback.answer("🚫 Однополые браки запрещены системой!", show_alert=True)
        return

    m_date = datetime.now().strftime("%d.%m.%Y")
    m_ts = int(time.time())
    gift = "Сердце Титана 💎"
    
    u1.update({
        "partner_id": callback.from_user.id, 
        "marriage_date": m_date, 
        "marriage_ts": m_ts, 
        "marriage_gift": gift
    })
    u2.update({
        "partner_id": i_id, 
        "marriage_date": m_date, 
        "marriage_ts": m_ts, 
        "marriage_gift": gift
    })
    db_save_all_records(master_cache)
    
    # ОФОРМЛЕНИЕ БРАКА
    num = random.randint(100, 999)
    if u1["theme"] == "Средневековая":
        lord_name = u1['name'] if u1['gender'] == 'М' else u2['name']
        lady_name = u1['name'] if u1['gender'] == 'Ж' else u2['name']
        lord_id = i_id if u1['gender'] == 'М' else callback.from_user.id
        lady_id = callback.from_user.id if u1['gender'] == 'М' else i_id
        
        res = (
            f"🏰 <b>КОРОЛЕВСКИЙ УКАЗ №{num}</b>\n\n"
            f"Сим объявляется священный союз двух сердец!\n"
            f"Поздравляем лорда <b>{lord_name}</b> и леди <b>{lady_name}</b>!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤴 Лорд: {get_user_mention_link(lord_id)}\n"
            f"👸 Леди: {get_user_mention_link(lady_id)}\n"
            f"📅 Дата: {m_date}\n"
            f"🎁 Дар: {gift}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Да пребудет с вами сила!"
        )
    else:
        partner1_label = get_gender_text(u1["gender"], 'partner')
        partner2_label = get_gender_text(u2["gender"], 'partner')
        res = (
            f"💍 <b>БРАК ЗАКЛЮЧЕН!</b>\n\n"
            f"Поздравляем молодоженов!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👰 {partner1_label}: {get_user_mention_link(i_id)}\n"
            f"🤵 {partner2_label}: {get_user_mention_link(callback.from_user.id)}\n"
            f"📅 Дата свадьбы: {m_date}\n"
            f"🎁 Свадебный подарок: {gift}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Желаем счастья и любви! ❤️"
        )

    await bot_instance.edit_message_text(
        inline_message_id=callback.inline_message_id, 
        text=res, 
        parse_mode="HTML"
    )

@dp_engine.callback_query(F.data.startswith("core_marry_no_"))
async def core_marry_reject(callback: CallbackQuery):
    """Отказ от предложения брака."""
    i_id = int(callback.data.split("_")[3])
    
    # Защита от самоотказа
    if callback.from_user.id == i_id:
        await callback.answer("❌ Вы не можете отклонить своё же предложение!", show_alert=True)
        return
    
    u_init = get_or_create_user(i_id)
    u_reject = get_or_create_user(callback.from_user.id, callback.from_user.first_name)
    
    is_medieval = (u_init["theme"] == "Средневековая")
    
    if is_medieval:
        reject_role = get_gender_text(u_reject["gender"], 'role')
        init_role = get_gender_text(u_init["gender"], 'role_lower')
        action = "отклонил" if u_reject["gender"] == "М" else "отклонила"
        res = (
            f"💔 <b>ОТКАЗ ОТ СОЮЗА</b>\n\n"
            f"{reject_role} <b>{u_reject['name']}</b> {action} предложение {init_role} <b>{u_init['name']}</b>.\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Сие решение окончательно и обжалованию не подлежит."
        )
    else:
        action = "отклонил" if u_reject["gender"] == "М" else "отклонила"
        res = (
            f"💔 <b>ПРЕДЛОЖЕНИЕ ОТКЛОНЕНО</b>\n\n"
            f"<b>{u_reject['name']}</b> {action} предложение <b>{u_init['name']}</b>.\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Возможно, это не судьба... 😔"
        )
    
    await bot_instance.edit_message_text(
        inline_message_id=callback.inline_message_id,
        text=res,
        parse_mode="HTML"
    )

@dp_engine.callback_query(F.data.startswith("core_child_add_"))
async def core_child_logic(callback: CallbackQuery):
    """Усыновление."""
    p_id = int(callback.data.split("_")[3])
    u_p1 = get_or_create_user(p_id)
    
    if not u_p1["partner_id"]: 
        await callback.answer("❌ Родитель должен быть в браке!", show_alert=True)
        return
    
    u_p2 = get_or_create_user(u_p1["partner_id"])
    
    # Защита от усыновления самого себя или своего партнера
    if callback.from_user.id in [p_id, u_p1["partner_id"]]:
        await callback.answer("❌ Вы не можете усыновить себя или своего супруга!", show_alert=True)
        return
    
    u_child = get_or_create_user(callback.from_user.id, callback.from_user.first_name)
    is_medieval = (u_p1["theme"] == "Средневековая")
    
    if callback.from_user.id not in u_p1["children_list"]:
        u_p1["children_list"].append(callback.from_user.id)
        u_p2["children_list"].append(callback.from_user.id)
        
        # Добавляем родителей ребенку
        if u_p1["gender"] == "М":
            u_child["parents"]["father"] = p_id
            u_child["parents"]["mother"] = u_p1["partner_id"]
        else:
            u_child["parents"]["mother"] = p_id
            u_child["parents"]["father"] = u_p1["partner_id"]
        
        db_save_all_records(master_cache)
    
    if is_medieval:
        p1_role = get_gender_text(u_p1["gender"], 'role_lower')
        p2_role = get_gender_text(u_p2["gender"], 'role_lower')
        child_status = "принят" if u_child.get("gender") == "М" else "принята"
        res = (
            f"👶 <b>УКАЗ О ПРИНЯТИИ НАСЛЕДНИКА</b>\n\n"
            f"{get_user_mention_link(callback.from_user.id)} {child_status} в королевскую семью {p1_role} <b>{u_p1['name']}</b> и {p2_role} <b>{u_p2['name']}</b>!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Да процветает великий род! 👑"
        )
    else:
        child_type = get_gender_text(u_child.get("gender"), 'child')
        res = (
            f"🍼 <b>УСЫНОВЛЕНИЕ ЗАВЕРШЕНО!</b>\n\n"
            f"{get_user_mention_link(callback.from_user.id)} теперь {child_type} семьи <b>{u_p1['name']}</b> и <b>{u_p2['name']}</b>!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Поздравляем с пополнением! 👨‍👩‍👧"
        )
        
    await bot_instance.edit_message_text(
        inline_message_id=callback.inline_message_id,
        text=res,
        parse_mode="HTML"
    )

# ==============================================================================
# [💔] МОДУЛЬ РАЗВОДА
# ==============================================================================
@dp_engine.callback_query(F.data == "btn_divorce_init")
async def divorce_init(callback: CallbackQuery):
    u = get_or_create_user(callback.from_user.id)
    if not u["partner_id"]:
        await callback.answer("❌ Вы и так свободны!", show_alert=True)
        return
    
    is_medieval = (u["theme"] == "Средневековая")
    
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="💔 Подтвердить развод", callback_data=f"core_div_final_{callback.from_user.id}"),
        types.InlineKeyboardButton(text="❌ Отменить", callback_data="btn_nav_main")
    ).as_markup()
    
    if is_medieval:
        role = get_gender_text(u["gender"], 'role')
        partner_msg = (
            f"⚠️ <b>КОРОЛЕВСКИЙ УКАЗ О РАСТОРЖЕНИИ СОЮЗА</b>\n\n"
            f"{role} <b>{u['name']}</b> желает расторгнуть священный союз.\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Подтверждаете ли вы данное решение?"
        )
    else:
        partner_label = get_gender_text(u["gender"], 'partner').lower()
        partner_msg = (
            f"⚠️ <b>ЗАПРОС НА РАЗВОД</b>\n\n"
            f"Ваш {partner_label} <b>{u['name']}</b> хочет развестись.\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Вы согласны?"
        )
    
    try:
        await bot_instance.send_message(
            u["partner_id"], 
            partner_msg, 
            reply_markup=kb,
            parse_mode="HTML"
        )
        await callback.message.edit_text(
            "📡 Запрос на развод отправлен партнеру. Ожидайте подтверждения.",
            reply_markup=build_back_button()
        )
    except:
        await callback.answer("❌ Не удалось отправить запрос партнеру!", show_alert=True)

@dp_engine.callback_query(F.data.startswith("core_div_final_"))
async def divorce_final(callback: CallbackQuery):
    req_id = int(callback.data.split("_")[3])
    u1, u2 = get_or_create_user(req_id), get_or_create_user(callback.from_user.id)
    
    is_medieval = (u1["theme"] == "Средневековая")
    
    # Убираем детям информацию о родителях
    for child_id in u1["children_list"]:
        child = get_or_create_user(child_id)
        child["parents"] = {"father": None, "mother": None}
    
    for user_ref in [u1, u2]:
        user_ref.update({
            "partner_id": None, 
            "love_points": 0, 
            "level": 1,
            "last_love_timestamp": 0,
            "marriage_date": None, 
            "marriage_ts": 0, 
            "marriage_gift": None,
            "children_list": [], 
            "inventory": [],
            "gifts_received": []
        })
    db_save_all_records(master_cache)
    
    if is_medieval:
        divorce_msg = (
            f"🥀 <b>СОЮЗ РАСТОРГНУТ</b>\n\n"
            f"Королевский брак официально аннулирован.\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Все регалии и очки славы обнулены."
        )
    else:
        divorce_msg = (
            f"💔 <b>РАЗВОД ОФОРМЛЕН</b>\n\n"
            f"Брак официально расторгнут.\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Весь прогресс обнулен."
        )
    
    await callback.message.edit_text(divorce_msg, reply_markup=build_back_button(), parse_mode="HTML")
    
    try: 
        await bot_instance.send_message(req_id, divorce_msg, parse_mode="HTML")
    except: 
        pass

# ==============================================================================
# [📜] РАЗВЕРНУТЫЙ СПРАВОЧНИК
# ==============================================================================
@dp_engine.callback_query(F.data == "btn_help_info")
async def help_info_render(callback: CallbackQuery):
    me = await bot_instance.get_me()
    guide = (
        f"📜 <b>ПОЛНОЕ РУКОВОДСТВО TITANIC MARRY</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Данный бот позволяет создавать союзы, растить детей и повышать свой статус в виртуальном мире.\n\n"
        f"<b>🚩 ОСНОВЫ ИГРЫ:</b>\n"
        f"Бот работает в <b>Инлайн-режиме</b>. Чтобы выполнить действие, начните писать <code>@{me.username}</code> в любом чате.\n\n"
        f"<b>💎 ДЕЙСТВИЯ И XP:</b>\n"
        f"• <b>Комплимент:</b> Выразите чувства партнеру. Дает <b>+25 XP</b> обоим. <b>КУЛДАУН: 1 ЧАС</b>\n"
        f"• <b>Сковорода:</b> Шуточный удар. <b>Не дает XP</b>. Без кулдауна — можно спамить!\n"
        f"• <b>Уровни:</b> Каждые 100 XP уровень вашей семьи растет (макс. 5). Каждый уровень дает награду в подарки.\n\n"
        f"<b>🛡 ЗАЩИТА ДЕЙСТВИЙ:</b>\n"
        f"Комплименты и удары сковородой можно совершать ТОЛЬКО со своим супругом! Попытка использовать их на других людях будет отклонена системой с сообщением 'Это не ваша пара!'.\n\n"
        f"<b>🎁 МАГАЗИН:</b>\n"
        f"В магазине можно покупать подарки за заработанные очки и дарить их своему супругу. Цены указаны прямо на кнопках. Подарки отображаются в профиле!\n\n"
        f"<b>🏆 ТОПЫ:</b>\n"
        f"• <b>Топ по времени</b> - пары с самым долгим браком\n"
        f"• <b>Топ по очкам</b> - пары с наибольшей суммой очков\n"
        f"• <b>Топ домов</b> - в разработке\n\n"
        f"<b>🍼 НАСЛЕДНИКИ:</b>\n"
        f"Вы можете усыновить любого участника чата. Он будет отображаться в вашем профиле как ребенок, а вы — как его родители.\n\n"
        f"<b>🏰 ТЕМЫ ОФОРМЛЕНИЯ:</b>\n"
        f"В настройках доступна Средневековая тема. Она меняет все уведомления на величественные королевские указы.\n\n"
        f"<b>🔒 ПРИВАТНОСТЬ:</b>\n"
        f"В настройках можно включить приватность профиля. Тогда другие пользователи не смогут просматривать ваш профиль.\n\n"
        f"<b>💔 РАЗВОД:</b>\n"
        f"При разводе подтверждение требуется от второй стороны. <b>ВНИМАНИЕ:</b> После развода все очки любви, уровни, подарки и список детей полностью стираются!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Разработано с любовью: {AUTHOR_LABEL}"
    )
    await callback.message.edit_text(guide, reply_markup=build_back_button(), parse_mode="HTML")

# ==============================================================================
# [⚙️] НАСТРОЙКИ
# ==============================================================================
@dp_engine.callback_query(F.data == "btn_settings_list")
async def settings_list(callback: CallbackQuery):
    u = get_or_create_user(callback.from_user.id)
    kb = InlineKeyboardBuilder()
    if not u["partner_id"]:
        kb.row(types.InlineKeyboardButton(text="⚧ Сменить пол", callback_data="cfg_sex_swap"))
    kb.row(types.InlineKeyboardButton(text="🏰 Средневековая", callback_data="cfg_theme_med"),
           types.InlineKeyboardButton(text="🏙 Обычная", callback_data="cfg_theme_norm"))
    
    # Кнопка приватности
    privacy_status = "🔓 Выкл" if not u.get("privacy", False) else "🔒 Вкл"
    kb.row(types.InlineKeyboardButton(text=f"Приватность: {privacy_status}", callback_data="cfg_privacy_toggle"))
    
    kb.row(types.InlineKeyboardButton(text="🔙 Назад", callback_data="btn_nav_main"))
    
    privacy_text = "включена" if u.get("privacy", False) else "выключена"
    
    await callback.message.edit_text(
        f"⚙️ <b>НАСТРОЙКИ ПРОФИЛЯ</b>\n\n"
        f"Тема: {u['theme']}\n"
        f"Ваш пол: {u['gender']}\n"
        f"Приватность: {privacy_text}",
        reply_markup=kb.as_markup(), 
        parse_mode="HTML"
    )

@dp_engine.callback_query(F.data == "cfg_sex_swap")
async def settings_sex(callback: CallbackQuery):
    u = get_or_create_user(callback.from_user.id)
    if not u["partner_id"]:
        u["gender"] = "Ж" if u["gender"] == "М" else "М"
        db_save_all_records(master_cache)
        await settings_list(callback)

@dp_engine.callback_query(F.data.startswith("cfg_theme_"))
async def settings_theme(callback: CallbackQuery):
    u = get_or_create_user(callback.from_user.id)
    u["theme"] = "Средневековая" if "med" in callback.data else "Обычная"
    db_save_all_records(master_cache)
    await settings_list(callback)

@dp_engine.callback_query(F.data == "cfg_privacy_toggle")
async def settings_privacy(callback: CallbackQuery):
    u = get_or_create_user(callback.from_user.id)
    u["privacy"] = not u.get("privacy", False)
    db_save_all_records(master_cache)
    await settings_list(callback)

@dp_engine.callback_query(F.data == "btn_nav_main")
async def nav_main(callback: CallbackQuery):
    if callback.message.photo:
        await callback.message.delete()
        await bot_instance.send_message(callback.from_user.id, "💍 <b>ГЛАВНОЕ МЕНЮ СИСТЕМЫ</b>", reply_markup=build_main_menu(), parse_mode="HTML")
    else:
        await callback.message.edit_text("💍 <b>ГЛАВНОЕ МЕНЮ СИСТЕМЫ</b>", reply_markup=build_main_menu(), parse_mode="HTML")

# ==============================================================================
# [🏁] ТОЧКА ВХОДА И ЗАПУСК (STARTUP)
# ==============================================================================
async def application_main_loop():
    """Инициализация и запуск бесконечного цикла опроса обновлений."""
    print("--------------------------------------------------")
    print("👑 TITANIC MARRY SYSTEM V10000 IS ACTIVE 👑")
    print(f"DEVELOPER: {AUTHOR_LABEL}")
    print("DATABASE: CONNECTED")
    print("--------------------------------------------------")
    
    db_storage_init()
    # Очистка старых обновлений перед запуском
    await bot_instance.delete_webhook(drop_pending_updates=True)
    # Запуск polling
    await dp_engine.start_polling(bot_instance)

if __name__ == "__main__":
    try:
        asyncio.run(application_main_loop())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот принудительно остановлен пользователем.")
