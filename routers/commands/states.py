from aiogram.fsm.state import StatesGroup, State

class Default(StatesGroup):
    default_state = State()

class Authorize(StatesGroup):
    waiting_server = State()

class Manage(StatesGroup):
    waiting_ip = State()
    waiting_command = State()

class Logs(StatesGroup):
    waiting_container_id_or_name = State()

class Start(StatesGroup):
    waiting_container_id_or_name = State()

class Restart(StatesGroup):
    waiting_container_id_or_name = State()

class Stop(StatesGroup):
    waiting_container_id_or_name = State()


class Remove(StatesGroup):
    server = State()


