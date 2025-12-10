"""
Telegram bot handlers for commands and callbacks.
"""
import logging
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from telebot.storage import StateRedisStorage
from telebot.asyncio_handler_backends import State

from app.config import settings
from app.bot.client import api_client
from app.bot.keyboards import (
    create_main_menu,
    create_start_keyboard,
    create_water_keyboard,
    create_carbs_type_keyboard,
    create_carbs_amount_keyboard,
    create_exercise_keyboard,
    create_progress_keyboard,
    create_settings_keyboard,
    create_cancel_keyboard,
    create_back_to_progress_keyboard
)
from app.bot.states import LoggingStates

logger = logging.getLogger(__name__)

# Initialize Redis storage with 5-minute TTL for conversation timeout
state_storage = StateRedisStorage(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
    prefix='telebot_state_'
)

# Initialize bot with state storage
bot = TeleBot(
    settings.TELEGRAM_BOT_TOKEN,
    threaded=False,
    state_storage=state_storage
)


def answer_callback(call_id: str, text: str):
    """Answer callback query with timeout handling"""
    try:
        bot.answer_callback_query(call_id, text, timeout=5)
    except Exception as e:
        logger.warning(f"Failed to answer callback: {e}")


# ============================================================================
# COMMAND HANDLERS
# ============================================================================

@bot.message_handler(commands=['start'])
def start_handler(message: Message):
    """Handle /start command"""
    try:
        # Create user via API
        user = api_client.create_user(
            telegram_user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        # Welcome message
        welcome_text = f"""
👋 Welcome {message.from_user.first_name}!

I'll help you track:
💧 Water intake (bottles)
🍽️ Carb consumption (portions)
🏃 Exercise sessions

Your default goals (tap Settings to change):
• Water: 3 bottles/day
• Carbs: Max 4 portions/day (meal=2, snack=1)
• Exercise: 6 sessions/week

Tap a button below to get started!
        """
        
        keyboard = create_start_keyboard()
        bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in start_handler: {e}", exc_info=True)
        bot.send_message(message.chat.id, "Sorry, something went wrong. Please try again.")


@bot.message_handler(commands=['progress'])
def progress_command_handler(message: Message):
    """Handle /progress command"""
    try:
        keyboard = create_progress_keyboard()
        bot.send_message(message.chat.id, "📊 Choose a view:", reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in progress_command_handler: {e}", exc_info=True)
        bot.send_message(message.chat.id, "Sorry, something went wrong. Please try again.")


@bot.message_handler(commands=['settings'])
def settings_command_handler(message: Message):
    """Handle /settings command"""
    try:
        keyboard = create_settings_keyboard()
        bot.send_message(message.chat.id, "⚙️ Settings:", reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in settings_command_handler: {e}", exc_info=True)
        bot.send_message(message.chat.id, "Sorry, something went wrong. Please try again.")


# ============================================================================
# MAIN MENU CALLBACKS
# ============================================================================

@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def main_menu_callback(call: CallbackQuery):
    """Return to main menu"""
    try:
        keyboard = create_main_menu()
        bot.edit_message_text(
            "Choose an action:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )
        answer_callback(call.id, "Main menu")
    except Exception as e:
        logger.error(f"Error in main_menu_callback: {e}", exc_info=True)
        answer_callback(call.id, "❌ Error occurred")


@bot.callback_query_handler(func=lambda call: call.data == "show_progress")
def show_progress_callback(call: CallbackQuery):
    """Show progress menu"""
    try:
        keyboard = create_progress_keyboard()
        bot.edit_message_text(
            "📊 Choose a view:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )
        answer_callback(call.id, "Progress")
    except Exception as e:
        logger.error(f"Error in show_progress_callback: {e}", exc_info=True)
        answer_callback(call.id, "❌ Error occurred")


@bot.callback_query_handler(func=lambda call: call.data == "show_settings")
def show_settings_callback(call: CallbackQuery):
    """Show settings menu"""
    try:
        keyboard = create_settings_keyboard()
        bot.edit_message_text(
            "⚙️ Settings:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )
        answer_callback(call.id, "Settings")
    except Exception as e:
        logger.error(f"Error in show_settings_callback: {e}", exc_info=True)
        answer_callback(call.id, "❌ Error occurred")


# ============================================================================
# WATER LOGGING HANDLERS
# ============================================================================

@bot.callback_query_handler(func=lambda call: call.data == "log_water")
def water_callback(call: CallbackQuery):
    """Show water logging options"""
    try:
        keyboard = create_water_keyboard()
        bot.edit_message_text(
            "💧 Water - How many bottles?",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )
        answer_callback(call.id, "Water")
    except Exception as e:
        logger.error(f"Error in water_callback: {e}", exc_info=True)
        answer_callback(call.id, "❌ Error occurred")


@bot.callback_query_handler(func=lambda call: call.data.startswith("water_add_") or call.data.startswith("water_sub_"))
def water_amount_callback(call: CallbackQuery):
    """Handle water amount logging"""
    try:
        # Parse callback data
        parts = call.data.split("_")
        action = parts[1]  # "add" or "sub"
        amount = int(parts[2])

        delta = amount if action == "add" else -amount

        # Log water via API
        result = api_client.log_water(
            telegram_user_id=call.from_user.id,
            delta=delta,
            message_id=call.message.message_id,
            idempotency_key=call.id
        )

        # Build response
        emoji = "✅" if result["goal_met"] else "💧"
        response = f"""
{emoji} Water logged!

Today: {result["new_total"]}/{result["goal"]} bottles
Remaining: {max(0, result["remaining"])} bottles
        """

        answer_callback(call.id, "✅ Logged!")
        keyboard = create_main_menu()
        bot.edit_message_text(
            response,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Error in water_amount_callback: {e}", exc_info=True)
        answer_callback(call.id, "❌ Error occurred")
        bot.send_message(call.message.chat.id, "Sorry, something went wrong. Please try again.")


# ============================================================================
# CARBS LOGGING HANDLERS
# ============================================================================

@bot.callback_query_handler(func=lambda call: call.data == "log_carbs")
def carbs_callback(call: CallbackQuery):
    """Show carbs type selection"""
    try:
        keyboard = create_carbs_type_keyboard()
        bot.edit_message_text(
            "🍽️ Carbs - Meal or Snack?",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )
        answer_callback(call.id, "Carbs")
    except Exception as e:
        logger.error(f"Error in carbs_callback: {e}", exc_info=True)
        answer_callback(call.id, "❌ Error occurred")


@bot.callback_query_handler(func=lambda call: call.data.startswith("carbs_type_"))
def carbs_type_callback(call: CallbackQuery):
    """Show carbs amount selection"""
    try:
        subtype = call.data.split("_")[-1]  # "meal" or "snack"

        keyboard = create_carbs_amount_keyboard(subtype)

        # Show helper text
        helper_text = "(Meal = 2 portions)" if subtype == "meal" else "(Snack = 1 portion)"

        bot.edit_message_text(
            f"🍽️ {subtype.capitalize()} {helper_text}\nHow many portions?",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )
        answer_callback(call.id, subtype.capitalize())

    except Exception as e:
        logger.error(f"Error in carbs_type_callback: {e}", exc_info=True)
        answer_callback(call.id, "❌ Error occurred")


@bot.callback_query_handler(func=lambda call: call.data.startswith("carbs_add_") or call.data.startswith("carbs_sub_"))
def carbs_amount_callback(call: CallbackQuery):
    """Handle carbs amount logging"""
    try:
        # Parse: carbs_add_meal_2 -> action=add, subtype=meal, amount=2
        parts = call.data.split("_")
        action = parts[1]  # "add" or "sub"
        subtype = parts[2]  # "meal" or "snack"
        amount = float(parts[3])

        delta = amount if action == "add" else -amount

        # Log carbs via API
        result = api_client.log_carbs(
            telegram_user_id=call.from_user.id,
            delta=delta,
            subtype=subtype,
            message_id=call.message.message_id,
            idempotency_key=call.id
        )

        # Build response
        emoji = "⚠️" if result["over_limit"] else "✅"
        warning = "\n⚠️ Over your daily limit!" if result["over_limit"] else ""

        response = f"""
{emoji} Carbs logged!

Today: {result["new_total"]}/{result["goal"]} portions
Remaining: {max(0, result["remaining"])} portions{warning}
        """

        answer_callback(call.id, "✅ Logged!")
        keyboard = create_main_menu()
        bot.edit_message_text(
            response,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Error in carbs_amount_callback: {e}", exc_info=True)
        answer_callback(call.id, "❌ Error occurred")
        bot.send_message(call.message.chat.id, "Sorry, something went wrong. Please try again.")


# ============================================================================
# EXERCISE LOGGING HANDLERS
# ============================================================================

@bot.callback_query_handler(func=lambda call: call.data == "log_exercise")
def exercise_callback(call: CallbackQuery):
    """Show exercise logging options"""
    try:
        keyboard = create_exercise_keyboard()
        bot.edit_message_text(
            "🏃 Exercise - How many sessions?",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )
        answer_callback(call.id, "Exercise")
    except Exception as e:
        logger.error(f"Error in exercise_callback: {e}", exc_info=True)
        answer_callback(call.id, "❌ Error occurred")


@bot.callback_query_handler(func=lambda call: call.data.startswith("exercise_add_") or call.data.startswith("exercise_sub_"))
def exercise_amount_callback(call: CallbackQuery):
    """Handle exercise amount logging"""
    try:
        # Parse callback data
        parts = call.data.split("_")
        action = parts[1]  # "add" or "sub"
        amount = int(parts[2])

        delta = amount if action == "add" else -amount

        # Log exercise via API
        result = api_client.log_exercise(
            telegram_user_id=call.from_user.id,
            delta=delta,
            message_id=call.message.message_id,
            idempotency_key=call.id
        )

        # Build response
        emoji = "✅" if result["new_total"] >= result["weekly_goal"] else "🏃"
        response = f"""
{emoji} Exercise logged!

This week: {result["new_total"]}/{result["weekly_goal"]} sessions
Remaining: {max(0, result["remaining"])} sessions
Week: {result["week_start"]} - {result["week_end"]}
        """

        answer_callback(call.id, "✅ Logged!")
        keyboard = create_main_menu()
        bot.edit_message_text(
            response,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Error in exercise_amount_callback: {e}", exc_info=True)
        answer_callback(call.id, "❌ Error occurred")
        bot.send_message(call.message.chat.id, "Sorry, something went wrong. Please try again.")


# ============================================================================
# PROGRESS DISPLAY HANDLERS
# ============================================================================

@bot.callback_query_handler(func=lambda call: call.data == "progress_today")
def progress_today_callback(call: CallbackQuery):
    """Show today's progress"""
    try:
        progress = api_client.get_today_progress(call.from_user.id)

        water_emoji = "✅" if progress["water"]["goal_met"] else "💧"
        carb_emoji = "✅" if not progress["carbs"]["over_limit"] else "⚠️"
        exercise_emoji = "✅" if progress["exercise"]["weekly_total"] >= progress["exercise"]["weekly_goal"] else "🏃"

        response = f"""
📊 Today's Progress ({progress["date"]})

{water_emoji} Water: {progress["water"]["current"]}/{progress["water"]["goal"]} bottles
   ({progress["water"]["percentage"]:.0f}% • {progress["water"]["remaining"]} remaining)

{carb_emoji} Carbs: {progress["carbs"]["current"]}/{progress["carbs"]["goal"]} portions
   ({progress["carbs"]["percentage"]:.0f}% • {progress["carbs"]["remaining"]} remaining)

{exercise_emoji} Exercise: {progress["exercise"]["weekly_total"]}/{progress["exercise"]["weekly_goal"]} sessions this week

🔥 Streaks:
   • Water: {progress["streaks"]["water_days"]} days
   • Carbs: {progress["streaks"]["carb_days"]} days
   • Both: {progress["streaks"]["combined_days"]} days
        """

        keyboard = create_back_to_progress_keyboard()
        bot.edit_message_text(
            response,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )
        answer_callback(call.id, "Today's progress")

    except Exception as e:
        logger.error(f"Error in progress_today_callback: {e}", exc_info=True)
        answer_callback(call.id, "❌ Error occurred")
        bot.send_message(call.message.chat.id, "Sorry, something went wrong. Please try again.")


# ============================================================================
# CUSTOM INPUT HANDLERS
# ============================================================================

@bot.callback_query_handler(func=lambda call: call.data == "water_custom")
def water_custom_callback(call: CallbackQuery):
    """Start custom water input flow"""
    try:
        bot.set_state(call.from_user.id, LoggingStates.waiting_water_amount, call.message.chat.id)

        keyboard = create_cancel_keyboard()
        bot.send_message(
            call.message.chat.id,
            "💧 Enter number of bottles (e.g., 1.5 or -0.5):",
            reply_markup=keyboard
        )
        answer_callback(call.id, "Custom water")

    except Exception as e:
        logger.error(f"Error in water_custom_callback: {e}", exc_info=True)
        answer_callback(call.id, "❌ Error occurred")


@bot.message_handler(state=LoggingStates.waiting_water_amount)
def water_custom_amount(message: Message):
    """Handle custom water amount input"""
    try:
        amount = float(message.text)
        if amount < -50 or amount > 50:
            raise ValueError("Amount out of range")

        result = api_client.log_water(
            telegram_user_id=message.from_user.id,
            delta=amount,
            message_id=message.message_id
        )

        response = f"✅ Logged {amount} bottles!\n\nToday: {result['new_total']}/{result['goal']} bottles"
        keyboard = create_main_menu()
        bot.send_message(message.chat.id, response, reply_markup=keyboard)

        bot.delete_state(message.from_user.id, message.chat.id)

    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid number. Please enter a valid amount (between -50 and 50):")
    except Exception as e:
        logger.error(f"Error in water_custom_amount: {e}", exc_info=True)
        bot.send_message(message.chat.id, "Sorry, something went wrong. Please try again.")
        bot.delete_state(message.from_user.id, message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("carbs_custom_"))
def carbs_custom_callback(call: CallbackQuery):
    """Start custom carbs input flow"""
    try:
        subtype = call.data.split("_")[-1]  # "meal" or "snack"

        # Store subtype in state data
        bot.set_state(call.from_user.id, LoggingStates.waiting_carb_amount, call.message.chat.id)

        # Store subtype in user data (using add_data)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['carb_subtype'] = subtype

        keyboard = create_cancel_keyboard()
        bot.send_message(
            call.message.chat.id,
            f"🍽️ Enter number of portions for {subtype} (e.g., 1.5 or -0.5):",
            reply_markup=keyboard
        )
        answer_callback(call.id, f"Custom {subtype}")

    except Exception as e:
        logger.error(f"Error in carbs_custom_callback: {e}", exc_info=True)
        answer_callback(call.id, "❌ Error occurred")


@bot.message_handler(state=LoggingStates.waiting_carb_amount)
def carbs_custom_amount(message: Message):
    """Handle custom carbs amount input"""
    try:
        amount = float(message.text)
        if amount < -50 or amount > 50:
            raise ValueError("Amount out of range")

        # Retrieve subtype from user data
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            subtype = data.get('carb_subtype', 'meal')

        result = api_client.log_carbs(
            telegram_user_id=message.from_user.id,
            delta=amount,
            subtype=subtype,
            message_id=message.message_id
        )

        warning = "\n⚠️ Over your daily limit!" if result["over_limit"] else ""
        response = f"✅ Logged {amount} portions ({subtype})!\n\nToday: {result['new_total']}/{result['goal']} portions{warning}"
        keyboard = create_main_menu()
        bot.send_message(message.chat.id, response, reply_markup=keyboard)

        bot.delete_state(message.from_user.id, message.chat.id)

    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid number. Please enter a valid amount (between -50 and 50):")
    except Exception as e:
        logger.error(f"Error in carbs_custom_amount: {e}", exc_info=True)
        bot.send_message(message.chat.id, "Sorry, something went wrong. Please try again.")
        bot.delete_state(message.from_user.id, message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "exercise_custom")
def exercise_custom_callback(call: CallbackQuery):
    """Start custom exercise input flow"""
    try:
        bot.set_state(call.from_user.id, LoggingStates.waiting_exercise_amount, call.message.chat.id)

        keyboard = create_cancel_keyboard()
        bot.send_message(
            call.message.chat.id,
            "🏃 Enter number of sessions (e.g., 3 or -1):",
            reply_markup=keyboard
        )
        answer_callback(call.id, "Custom exercise")

    except Exception as e:
        logger.error(f"Error in exercise_custom_callback: {e}", exc_info=True)
        answer_callback(call.id, "❌ Error occurred")


@bot.message_handler(state=LoggingStates.waiting_exercise_amount)
def exercise_custom_amount(message: Message):
    """Handle custom exercise amount input"""
    try:
        amount = int(message.text)
        if amount < -100 or amount > 100:
            raise ValueError("Amount out of range")

        result = api_client.log_exercise(
            telegram_user_id=message.from_user.id,
            delta=amount,
            message_id=message.message_id
        )

        response = f"✅ Logged {amount} sessions!\n\nThis week: {result['new_total']}/{result['weekly_goal']} sessions"
        keyboard = create_main_menu()
        bot.send_message(message.chat.id, response, reply_markup=keyboard)

        bot.delete_state(message.from_user.id, message.chat.id)

    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid number. Please enter a valid integer (between -100 and 100):")
    except Exception as e:
        logger.error(f"Error in exercise_custom_amount: {e}", exc_info=True)
        bot.send_message(message.chat.id, "Sorry, something went wrong. Please try again.")
        bot.delete_state(message.from_user.id, message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "cancel_input")
def cancel_input_callback(call: CallbackQuery):
    """Cancel any active input state and return to main menu"""
    try:
        bot.delete_state(call.from_user.id, call.message.chat.id)
        answer_callback(call.id, "❌ Cancelled")

        keyboard = create_main_menu()
        bot.edit_message_text(
            "❌ Cancelled. Choose an action:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Error in cancel_input_callback: {e}", exc_info=True)
        answer_callback(call.id, "❌ Error occurred")


# ============================================================================
# SETTINGS HANDLERS (Placeholder - redirect to web app)
# ============================================================================

@bot.callback_query_handler(func=lambda call: call.data == "settings_goals")
def settings_goals_callback(call: CallbackQuery):
    """Redirect to web app for goal editing"""
    try:
        bot.answer_callback_query(
            call.id,
            "Please use the web app to edit goals",
            show_alert=True
        )
    except Exception as e:
        logger.error(f"Error in settings_goals_callback: {e}", exc_info=True)


@bot.callback_query_handler(func=lambda call: call.data == "settings_notifications")
def settings_notifications_callback(call: CallbackQuery):
    """Redirect to web app for notification settings"""
    try:
        bot.answer_callback_query(
            call.id,
            "Please use the web app to manage notifications",
            show_alert=True
        )
    except Exception as e:
        logger.error(f"Error in settings_notifications_callback: {e}", exc_info=True)

