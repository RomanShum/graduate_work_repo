import asyncio
import websockets

peoples = {}  # Словарь будет содержать ник подключившегося человека и указатель на его websocket-соединение.

async def welcome(websocket: websockets.ServerConnection) -> str:
    # При подключении к серверу попросим указать свой ник и пополним им словарь peoples
    await websocket.send('Представьтесь!')
    name = await websocket.recv()
    await websocket.send('Чтобы поговорить, напишите "<имя>: <сообщение>". Например: Ира: купи хлеб.')
    await websocket.send('Посмотреть список участников можно командой "?"')
    peoples[name.strip()] = websocket
    return name

async def receiver(websocket: websockets.ServerConnection) -> None:
    name = await welcome(websocket)
    try:
        while True:
            # Получаем сообщение от абонента и решаем, что с ним делать
            message = (await websocket.recv()).strip()
            if message == '?':  # На знак вопроса вернём список ников подключившихся людей
                await websocket.send(', '.join(peoples.keys()))
                continue
            else:  # Остальные сообщения попытаемся проанализировать и отправить нужному собеседнику
                try:
                    to, text = message.split(': ', 1)
                    if to in peoples:
                        # Пересылаем сообщение в канал получателя, указав отправителя
                        await peoples[to].send(f'Сообщение от {name}: {text}')
                    else:
                        await websocket.send(f'Пользователь {to} не найден')
                except ValueError:
                    await websocket.send('Неверный формат сообщения. Используйте "имя: сообщение"')
    except websockets.exceptions.ConnectionClosed:
        # Удаляем пользователя при отключении
        if name in peoples:
            del peoples[name]
        print(f"Пользователь {name} отключился")

async def main():
    # Создаём сервер, который будет обрабатывать подключения
    async with websockets.serve(receiver, "localhost", 8765, origins=None):
        print("WebSocket сервер запущен на ws://localhost:8765")
        print("Ожидание подключений...")
        # Бесконечно держим сервер запущенным
        await asyncio.Future()  # Работает как loop.run_forever()

if __name__ == '__main__':
    asyncio.run(main())