"""
Bot conversation states for custom input flows.
"""
from telebot.handler_backends import State, StatesGroup


class LoggingStates(StatesGroup):
    """States for logging custom amounts"""
    waiting_water_amount = State()
    waiting_carb_amount = State()
    waiting_exercise_amount = State()

