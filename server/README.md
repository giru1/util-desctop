# Efirit Plugin WebServer

Web server предназначен для отправки json-заданий на ККТ.
Поддерживаемые производители:

- АТОЛ (дККТ10)

## Возможности

- Отправка JSON заданий и получение ответа
- Открытие и закрытие соединения с кассой

## Запуск и работа

В первую очередь для работы необходимо установить драйвер ККТ.
Файл с настройками сервера должен быть расположен в папке с проектом.

config.json

```json
{
  "manufacture": 1,
  "lib_path": "",
  "conn_type": 2,
  "ip_address": "85.192.132.219",
  "ip_port": 5555,
  "com_file": 1
}
```

Установка зависимостей

```sh
pip install -r requirements.txt
```

Запуск dev сервера используя cli

```sh
uvicorn main:app --reload --port 8000
```

Запуск сервера программно, используя модуль uvicorn server

```py

config = Config("main:app", port=8001, log_level="info")
server = UvicornServer(config=config)
server.start()
...
server.stop()

```

## Документация

[Описание JSON заданий драйвера АТОЛ](https://integration.atol.ru/api/#json-tasks)
Документация API доступна при запущенном сервере [здесь](http://localhost:8001/docs)
