#
# Серверное приложение для соединений
#
import asyncio


class ServerProtocol(asyncio.Protocol):
    login: str = None  # логин пользователя
    server: 'Server'  # сервер
    transport: None  # подключение

    def __init__(self, server: 'Server'):  # инициализация класса
        self.server = server

    def data_received(self, data: bytes):  # обработка полученных данных
        print(data)

        try:  # попытка декодировать данные
            decoded = data.decode()
        except:  # если деодировать данные невозможно вывет=сти сообщение, деокдированные данные None
            print("невозможно декодировать текст")
            decoded = None

        if decoded is not None:  # если данные декодированы
            if self.login is not None:  # если пользователь зарегестрирован отправить сообщение
                self.send_message(decoded)
            else:  # если у пользователя нет логина создать логин
                self.login = self.create_login(decoded)

    def connection_made(self, transport):  # присоедеинени нового пользователя
        self.server.clients.append(self)  # добавить пользователя в список пользователей
        self.transport = transport
        print("пришел новый клиент")

    def connection_lost(self, exc: Exception):  # отключения пользователя
        self.server.clients.remove(self)  # удалить пользователя из списка
        print("Клиент вышел")

    def send_message(self, content: str):  # отправка сообщения
        message = f"{self.login}: {content}\n"  # формирвание сообщения

        self.save_message(message)  # сохранить сообщение в историю

        for user in self.server.clients:  # отправить сообщение всем пользователям
            user.transport.write(message.encode())

    def save_message(self, message):  # сохранения истории сообщений
        self.server.message_history.append(message)  # добавить сообщение в историю

        if len(self.server.message_history) > 10:  # ограничение на количество сообщений в истории
            self.server.message_history = self.server.message_history[1:]

    def load_message(self):  # загрузка истории сообщений
        for message in self.server.message_history:  # отправить все сообщения из истории
            self.transport.write(message.encode())

    def create_login(self, decoded):  # создать логин для пользователя
        if decoded.startswith("login:"):  # если введена команда login: "логин"
            user_login = decoded.replace("login: ", "").replace("\r\n", "")  # формирования логина пользователя

            if user_login not in self.server.get_login_list():  # проверка уникальности логина
                self.transport.write(f"привет, {user_login}!\n".encode())  # прииветсвия пользователя
                self.load_message()  # загрузка истории сообщений

                return user_login  # возврат логина
            else:
                self.transport.write(f"привет, Такой логин уже существует!\n".encode())  # сообщение что такой логин уже существует

                return None
        else:
            self.transport.write(f"Неправильный логин!\n".encode())  # сообщение о неправильно введеном логине

            return None


class Server:
    clients: list  # список пользователй
    message_history: list  # история сообщений

    def __init__(self):  # инициализация класса
        self.clients = []
        self.message_history = []

    def build_protocol(self):  # протокол передачи данных
        return ServerProtocol(self)

    def get_login_list(self):  # возврат списка логинов зарегестрированных пользователей
        login_list = []  # списко логинов
        for user in self.clients:  # для каждого пользователя добавить логин
            login_list.append(user.login)

        return login_list  # вернуть список логинов

    async def star(self):  # запуск сервера
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.build_protocol,  # протокол
            '127.0.0.1',  # адрес сервера
            9999  # порт
        )

        print("сервер запущен ...")

        await coroutine.serve_forever()


process = Server()  # процесс сервера

try:
    asyncio.run(process.star())  # запуск сервера
except KeyboardInterrupt:  # исклбчение для отключения сервера
    print("Сервер остановлен вручную")




