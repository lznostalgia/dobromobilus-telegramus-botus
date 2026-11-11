from aiogram.fsm.state import State, StatesGroup


class UserFlow(StatesGroup):
  "Машина состояний обычного пользователя: Вид Питомца, Город, Выбор Питомца, Подтверждение Заявки"
  choosing_species = State()
  choosing_city = State()
  choosing_pet = State()
  confirming = State()