"""
Inline keyboard layouts for the Telegram bot.
"""
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.config import settings


def create_main_menu() -> InlineKeyboardMarkup:
    """Create main menu keyboard"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("💧 Water", callback_data="log_water"),
        InlineKeyboardButton("🍽️ Carbs", callback_data="log_carbs")
    )
    keyboard.row(
        InlineKeyboardButton("🏃 Exercise", callback_data="log_exercise"),
        InlineKeyboardButton("📊 Progress", callback_data="show_progress")
    )
    keyboard.row(InlineKeyboardButton("⚙️ Settings", callback_data="show_settings"))
    return keyboard


def create_water_keyboard() -> InlineKeyboardMarkup:
    """Create water logging keyboard"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("+1 🚰", callback_data="water_add_1"),
        InlineKeyboardButton("+2 🚰", callback_data="water_add_2"),
        InlineKeyboardButton("+3 🚰", callback_data="water_add_3")
    )
    keyboard.row(
        InlineKeyboardButton("-1 🚰", callback_data="water_sub_1"),
        InlineKeyboardButton("Custom", callback_data="water_custom")
    )
    keyboard.row(InlineKeyboardButton("« Back", callback_data="main_menu"))
    return keyboard


def create_carbs_type_keyboard() -> InlineKeyboardMarkup:
    """Create carbs type selection keyboard"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🍽️ Meal (2 portions)", callback_data="carbs_type_meal"),
        InlineKeyboardButton("🍪 Snack (1 portion)", callback_data="carbs_type_snack")
    )
    keyboard.row(InlineKeyboardButton("« Back", callback_data="main_menu"))
    return keyboard


def create_carbs_amount_keyboard(subtype: str) -> InlineKeyboardMarkup:
    """Create carbs amount selection keyboard"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("+2", callback_data=f"carbs_add_{subtype}_2"),
        InlineKeyboardButton("+1.5", callback_data=f"carbs_add_{subtype}_1.5"),
        InlineKeyboardButton("+1", callback_data=f"carbs_add_{subtype}_1"),
        InlineKeyboardButton("+0.5", callback_data=f"carbs_add_{subtype}_0.5")
    )
    keyboard.row(
        InlineKeyboardButton("-2", callback_data=f"carbs_sub_{subtype}_2"),
        InlineKeyboardButton("-1.5", callback_data=f"carbs_sub_{subtype}_1.5"),
        InlineKeyboardButton("-1", callback_data=f"carbs_sub_{subtype}_1"),
        InlineKeyboardButton("-0.5", callback_data=f"carbs_sub_{subtype}_0.5")
    )
    keyboard.row(
        InlineKeyboardButton("Custom", callback_data=f"carbs_custom_{subtype}")
    )
    keyboard.row(InlineKeyboardButton("« Back", callback_data="log_carbs"))
    return keyboard


def create_exercise_keyboard() -> InlineKeyboardMarkup:
    """Create exercise logging keyboard"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("+1 session", callback_data="exercise_add_1"),
        InlineKeyboardButton("+2 sessions", callback_data="exercise_add_2")
    )
    keyboard.row(
        InlineKeyboardButton("-1 session", callback_data="exercise_sub_1"),
        InlineKeyboardButton("Custom", callback_data="exercise_custom")
    )
    keyboard.row(InlineKeyboardButton("« Back", callback_data="main_menu"))
    return keyboard


def create_progress_keyboard() -> InlineKeyboardMarkup:
    """Create progress menu keyboard"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📊 Today", callback_data="progress_today"),
        InlineKeyboardButton("🏃 This Week", callback_data="progress_exercise_week")
    )
    keyboard.row(
        InlineKeyboardButton("📈 Monthly Report", url=f"{settings.WEB_APP_URL}/reports")
    )
    keyboard.row(InlineKeyboardButton("« Back", callback_data="main_menu"))
    return keyboard


def create_settings_keyboard() -> InlineKeyboardMarkup:
    """Create settings menu keyboard"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("🎯 Edit Goals", callback_data="settings_goals"))
    keyboard.row(InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications"))
    keyboard.row(InlineKeyboardButton("🌐 Open Web App", url=f"{settings.WEB_APP_URL}"))
    keyboard.row(InlineKeyboardButton("« Back", callback_data="main_menu"))
    return keyboard


def create_cancel_keyboard() -> InlineKeyboardMarkup:
    """Create cancel keyboard for custom input"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("❌ Cancel", callback_data="cancel_input"))
    return keyboard


def create_back_to_progress_keyboard() -> InlineKeyboardMarkup:
    """Create back to progress keyboard"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("« Back", callback_data="show_progress"))
    return keyboard


def create_start_keyboard() -> InlineKeyboardMarkup:
    """Create start/welcome keyboard with web app link"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🌐 Open Web App", url=f"{settings.WEB_APP_URL}")
    )
    keyboard.row(
        InlineKeyboardButton("💧 Water", callback_data="log_water"),
        InlineKeyboardButton("🍽️ Carbs", callback_data="log_carbs")
    )
    keyboard.row(
        InlineKeyboardButton("🏃 Exercise", callback_data="log_exercise"),
        InlineKeyboardButton("📊 Progress", callback_data="show_progress")
    )
    keyboard.row(InlineKeyboardButton("⚙️ Settings", callback_data="show_settings"))
    return keyboard

