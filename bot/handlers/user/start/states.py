from aiogram.fsm.state import State, StatesGroup


class StartCommandStates(StatesGroup):
    waiting_for_vendor_code = State()
    waiting_for_vendor_code_and_keyword = State()
