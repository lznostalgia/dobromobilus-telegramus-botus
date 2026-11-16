from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    choosing_animal_type = State()
    choosing_city = State()
    choosing_shelter = State()
    choosing_pet = State()
    viewing_pet = State()
    confirming_application = State()