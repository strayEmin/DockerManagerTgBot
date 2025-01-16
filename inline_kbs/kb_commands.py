from dataclasses import dataclass


@dataclass
class CommandForInlineKB:
    label: str
    data: str


COMMAND_GET_LIST_OF_RUNNING = CommandForInlineKB(
    label = "Список запущенных контейнеров",
    data = "running_list"
)
COMMAND_GET_LIST_OF_ALL = CommandForInlineKB(
    label = "Список всех контейнеров",
    data = "all_list"
)
COMMAND_START_CONTAINER = CommandForInlineKB(
    label = "Запуск остановленного контейнера",
    data = "start_container"
)
COMMAND_RESTART_CONTAINER = CommandForInlineKB(
    label = "Перезапуск контейнера",
    data = "restart_container"
)
COMMAND_STOP_CONTAINER = CommandForInlineKB(
    label = "Остановка контейнера",
    data = "stop_container"
)
COMMAND_GET_LOGS_DOCKER = CommandForInlineKB(
    label = "Логи контейнера за последний час",
    data = "logs_container"
)
COMMAND_GET_DOCKER_STATS = CommandForInlineKB(
    label = "Использование ресурсов системы сейчас",
    data = "stats"
)
COMMAND_CANCEL = CommandForInlineKB(
    label = "Отмена (вернуться в начало)",
    data = "cancel"
)
COMMANDS_LIST = [
    COMMAND_GET_LIST_OF_RUNNING,
    COMMAND_GET_LIST_OF_ALL,
    COMMAND_START_CONTAINER,
    COMMAND_RESTART_CONTAINER,
    COMMAND_STOP_CONTAINER,
    COMMAND_GET_LOGS_DOCKER,
    COMMAND_GET_DOCKER_STATS
]
