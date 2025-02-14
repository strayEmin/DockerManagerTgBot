start_text = """Этот бот предназначен для управления контейнерами докер на удаленном сервере.
С вашей стороны перед началом работы требуется добавить публичный SSH-ключ на сервер вручную (подробнее - /authorize) \
и пользоваться ботом в свое удовольствие. В целях безопасности не были реализованы функции удаления контейнера, \
загрузки и запуска новых контейнеров с помощью image'й, то есть все безвозвратные или потенциально вредоносные действия.
Бот не хранит никакие пользовательские данные, кроме данных, по которым осуществляется вход (IP-адрес, имя пользователя и номер порта)\
ради удобства пользования.
Для начала работы или получения списка основных доступных команд, не относящимися непосредственно к докер, введите /help."""
help_text = """
Список доступных команд с кратким описанием:
/start - начало взаимодействия
/help - выводит это сообщение
/authorize - добавление сервера
/manage - управление контейнерами докер
/rmserver - удаление авторизованного сервера из базы данных
"""
