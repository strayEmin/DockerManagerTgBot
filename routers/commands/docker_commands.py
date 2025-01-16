import io
import datetime
import asyncssh

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import types

from bot_config import PATH_TO_CLIENT_KEYS, SSHPubKey
from inline_kbs.inline_kb_builders import build_choice_ip_kb, build_choice_command_kb
from inline_kbs.kb_commands import *
from validation.validation import validate_connection_string, is_valid_docker_id_or_name
from texts import help_text
from .states import *
from database.db import *


router = Router(name=__name__)


async def conn_is_successful(ip: str, port: int = 22, username: str ="root") -> bool:
    try:
        conn = await asyncssh.connect(ip, port=port, username=username, client_keys=[PATH_TO_CLIENT_KEYS], known_hosts=None)
        conn.close()
        return True
    except (asyncssh.Error, OSError):
        return False


def parse_connection_string(connection_string) -> dict:
    result = {"username": "root", "ip": "", "port": 22}

    if ':' in connection_string:
        connection_string, port = connection_string.rsplit(':', 1)
        if port.isdigit():
            result["port"] = int(port)

    if '@' in connection_string:
        username, ip = connection_string.split('@', 1)
        result["username"] = username if username else result["username"]
        result["ip"] = ip
    else:
        result["ip"] = connection_string

    return result


async def send_file_with_output_by_call(callback: CallbackQuery, output: str, caption:str = ''):
    file = io.StringIO()
    file.write(output)
    await callback.message.answer_document(
        caption=caption,
        document=types.BufferedInputFile(
            file=file.getvalue().encode("utf-8"),
            filename="output.txt"
        )
    )



async def send_file_with_output_by_message(message: Message, output: str, caption:str = ''):
    file = io.StringIO()
    file.write(output)
    await message.answer_document(
        caption=caption,
        document=types.BufferedInputFile(
            file=file.getvalue().encode("utf-8"),
            filename="output.txt"
        )
    )


async def run_ssh_command_and_send_result_by_call(callback: CallbackQuery,
                                                  server_dict: dict,
                                                  command: str,
                                                  file_caption: str):
    try:
        async with asyncssh.connect(server_dict["ip"], port=server_dict["port"], username=server_dict["username"],
                                    client_keys=[PATH_TO_CLIENT_KEYS], known_hosts=None) as conn:
            try:
                result = await conn.run(f"{command}", check=True)
            except asyncssh.ProcessError as process_exc:
                await send_file_with_output_by_call(callback, process_exc.stderr,
                                                       caption="Процесс закончился с ошибкой, подробнее в файле")
            else:
                await send_file_with_output_by_call(callback, result.stdout,
                                                       caption=file_caption)
    except (asyncssh.Error, OSError):
        await callback.message.answer("Ошибка SSH соединения")


async def run_ssh_command_and_send_result_by_message(message: Message,
                                                  server_dict: dict,
                                                  command: str,
                                                  file_caption: str):
    try:
        async with asyncssh.connect(server_dict["ip"], port=server_dict["port"], username=server_dict["username"],
                                    client_keys=[PATH_TO_CLIENT_KEYS], known_hosts=None) as conn:
            try:
                result = await conn.run(command, check=True)
            except asyncssh.ProcessError as process_exc:
                await send_file_with_output_by_message(message, process_exc.stderr,
                                                       caption="Процесс закончился с ошибкой, подробнее в файле")
            else:
                await send_file_with_output_by_message(message, result.stdout,
                                                       caption=file_caption)
    except (asyncssh.Error, OSError):
        await message.answer("Ошибка SSH соединения")


# обработка нажатия кнопки отмена, всегда стоит выше остальных обработчиков
@router.callback_query(F.data == COMMAND_CANCEL.data)
async def handle_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()
    await callback.message.answer(help_text)


authorize_text = ("Управление докер-контейнерами осуществляется с помощью протокола SSH.\n"
            "Для подключения к вашему серверу потребуется IP адрес сервера, а так же "
            "добавление SSH ключа в файл authorized_keys и настроенная конфигурация SSH-daemon, "
            "позволяющая подключение с root правами по ключу.\n"
            "По понятным причинам, бот не будет корректно работать с динамическим IP.\n"
            "Введите IP адрес сервера, на котором нужно осуществлять управление и номер порта, "
            "на котором работает SSH-daemon(если он отличается от стандартного 22 порта), а так же, если подключение по SSH с username ='root'"
            " недоступен, введите username, заменяющий его.\n"
            "Формат ввода: USERNAME@IP:PORT")


@router.message(Command("authorize"))
async def handle_authorize(message: Message, state: FSMContext):
    await state.set_state(Authorize.waiting_server)
    file = io.StringIO()
    file.write(SSHPubKey)
    await message.answer_document(
        caption=authorize_text,
        document=types.BufferedInputFile(
            file=file.getvalue().encode("utf-8"),
            filename="ssh_pubkey.txt"
        ),
        reply_markup=build_choice_command_kb()
    )



@router.message(Authorize.waiting_server)
async def handle_address(message: Message, state: FSMContext):
    text_of_input = message.text.strip()
    if not validate_connection_string(text_of_input):
        await state.clear()
        await message.answer("Некорректный ввод")
    else:
        conn_data = parse_connection_string(text_of_input)
        print(conn_data["ip"], conn_data["port"], conn_data["username"])
        is_successful = await conn_is_successful(conn_data["ip"], conn_data["port"], conn_data["username"])
        if is_successful:
            await add_user_ip(str(message.from_user.id), conn_data["username"] + "@" + conn_data["ip"] + ":" +
                              str(conn_data["port"]))
            await message.answer("Попытка подключения успешна, адрес записан.")
            await state.clear()
        else:
            await message.answer("Ошибка подключения: введен неверный IP, номер порта или неправильно настроен сервер.")
            await state.clear()


@router.message(Command("manage"))
async def handle_manage(message: Message, state: FSMContext):
    users_ip_and_ports = await get_ips_by_user_id(str(message.from_user.id))
    if not users_ip_and_ports:
        await state.clear()
        await message.answer(
            "Не найдено авторизованных вами IP адресов. Воспользуйтесь командой /authorize"
        )
    else:
        await state.set_state(Manage.waiting_ip)
        await message.answer(
            "На каком из ваших IP адресов требуется осуществить управление?",
            reply_markup=build_choice_ip_kb(users_ip_and_ports)
        )


@router.callback_query(Manage.waiting_ip)
async def handle_choice_of_ip(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    conn_data = parse_connection_string(callback.data)
    if not await conn_is_successful(conn_data["ip"], conn_data["port"], conn_data["username"]):
        await callback.message.answer("Выбранный IP недоступен.")
        await state.clear()
    else:
        await state.update_data(ip=callback.data)
        await state.set_state(Manage.waiting_command)
        await callback.message.answer(
            "Подключение успешно, выберите действие:",
            reply_markup=build_choice_command_kb(COMMANDS_LIST)
        )


@router.callback_query(F.data == COMMAND_GET_LIST_OF_RUNNING.data, Manage.waiting_command)
async def handle_get_list_of_running_containers_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    data = await state.get_data()
    server = parse_connection_string(data["ip"])

    await run_ssh_command_and_send_result_by_call(
        callback=callback,
        server_dict=server,
        command="sudo docker ps",
        file_caption=f"Успешно, список запущенных контейнеров по на сервере по ip {server["ip"]} в файле"
    )

    await state.clear()


@router.callback_query(F.data == COMMAND_GET_LIST_OF_ALL.data, Manage.waiting_command)
async def handle_list_of_all_containers_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    data = await state.get_data()
    server = parse_connection_string(data["ip"])

    await run_ssh_command_and_send_result_by_call(
        callback=callback,
        server_dict=server,
        command="sudo docker ps -a",
        file_caption=f"Успешно, список всех контейнеров по на сервере по ip {server["ip"]} в файле"
    )

    await state.clear()


@router.message(Command("rmserver"))
async def handle_remove_server_command(message: Message, state: FSMContext):
    users_ip_and_ports = await get_ips_by_user_id(str(message.from_user.id))
    if not users_ip_and_ports:
        await state.clear()
        await message.answer(
            "Не найдено авторизованных вами серверов."
        )
    else:
        await state.set_state(Remove.server)
        await message.answer(
            "Какой из ваших серверов подлежит удалению?",
            reply_markup=build_choice_ip_kb(users_ip_and_ports)
        )


@router.callback_query(Remove.server)
async def remove_ip(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await delete_user_ip(str(callback.from_user.id), callback.data)
    await state.clear()
    server = parse_connection_string(callback.data)
    await callback.message.answer(f"Сервер по IP {server["ip"]}, username '{server["username"]}', port {server["port"]} удален из базы данных успешно.")


@router.callback_query(F.data == COMMAND_GET_LOGS_DOCKER.data, Manage.waiting_command)
async def handle_logs_of_container_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(Logs.waiting_container_id_or_name)
    await callback.message.answer("Введите ID или имя контейнера, логи которого хотите посмотреть",
                                  reply_markup=build_choice_command_kb())


@router.message(Logs.waiting_container_id_or_name)
async def answer_logs(message: Message, state: FSMContext):
    if not is_valid_docker_id_or_name(message.text):
        await message.answer("Введен некорректный идентификатор (имя или ID контейнера), попробуйте еще раз",
                             reply_markup=build_choice_command_kb())
        await state.set_state(Logs.waiting_container_id_or_name)
    else:
        data = await state.get_data()
        server = parse_connection_string(data["ip"])

        await run_ssh_command_and_send_result_by_message(
            message=message,
            server_dict=server,
            command=f"sudo docker logs --since 60m -t {message.text}",
            file_caption=f"Успешно, логи контейнера {message.text} по ip {server["ip"]} за последний час в файле"
        )

        await state.clear()


@router.callback_query(F.data == COMMAND_GET_DOCKER_STATS.data, Manage.waiting_command)
async def handle_stats_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    data = await state.get_data()
    server = parse_connection_string(data["ip"])

    await run_ssh_command_and_send_result_by_call(
        callback=callback,
        server_dict=server,
        command="sudo docker stats --no-stream",
        file_caption=f"Успешно, использование ресурсов на момент {datetime.datetime.now().time()} по ip {server["ip"]} в файле"
    )

    await state.clear()


@router.callback_query(F.data == COMMAND_START_CONTAINER.data, Manage.waiting_command)
async def handle_container_start_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(Start.waiting_container_id_or_name)
    await callback.message.answer("Введите ID или имя контейнера, который хотите запустить",
                                  reply_markup=build_choice_command_kb())


@router.message(Start.waiting_container_id_or_name)
async def answer_start_result(message: Message, state: FSMContext):
    if not is_valid_docker_id_or_name(message.text):
        await message.answer("Введен некорректный идентификатор (имя или ID контейнера), попробуйте еще раз",
                             reply_markup=build_choice_command_kb())
        await state.set_state(Start.waiting_container_id_or_name)
    else:
        data = await state.get_data()
        server = parse_connection_string(data["ip"])

        await run_ssh_command_and_send_result_by_message(
            message=message,
            server_dict=server,
            command=f"sudo docker start {message.text}",
            file_caption=f"Успешно, контейнер {message.text} запущен"
        )

        await state.clear()


@router.callback_query(F.data == COMMAND_RESTART_CONTAINER.data, Manage.waiting_command)
async def handle_container_restart_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(Restart.waiting_container_id_or_name)
    await callback.message.answer("Введите ID или имя контейнера, который хотите перезапустить",
                                  reply_markup=build_choice_command_kb())


@router.message(Restart.waiting_container_id_or_name)
async def answer_restart_result(message: Message, state: FSMContext):
    if not is_valid_docker_id_or_name(message.text):
        await message.answer("Введен некорректный идентификатор (имя или ID контейнера), попробуйте еще раз",
                             reply_markup=build_choice_command_kb())
        await state.set_state(Restart.waiting_container_id_or_name)
    else:
        data = await state.get_data()
        server = parse_connection_string(data["ip"])

        await run_ssh_command_and_send_result_by_message(
            message=message,
            server_dict=server,
            command=f"sudo docker restart {message.text}",
            file_caption=f"Успешно, контейнер {message.text} перезапущен"
        )

        await state.clear()


@router.callback_query(F.data == COMMAND_STOP_CONTAINER.data, Manage.waiting_command)
async def handle_container_restart_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(Stop.waiting_container_id_or_name)
    await callback.message.answer("Введите ID или имя контейнера, который хотите остановить",
                                  reply_markup=build_choice_command_kb())


@router.message(Stop.waiting_container_id_or_name)
async def answer_stop_result(message: Message, state: FSMContext):
    if not is_valid_docker_id_or_name(message.text):
        await message.answer("Введен некорректный идентификатор (имя или ID контейнера), попробуйте еще раз",
                             reply_markup=build_choice_command_kb())
        await state.set_state(Stop.waiting_container_id_or_name)
    else:
        data = await state.get_data()
        server = parse_connection_string(data["ip"])

        await run_ssh_command_and_send_result_by_message(
            message=message,
            server_dict=server,
            command=f"sudo docker stop {message.text}",
            file_caption=f"Успешно, контейнер {message.text} остановлен"
        )

        await state.clear()