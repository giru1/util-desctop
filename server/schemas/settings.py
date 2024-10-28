import json
import os
from enum import IntEnum

from pydantic import BaseModel, Field


class Manufacture(IntEnum):
    ATOL = 1
    EVOTOR = 2


class ConnectionType(IntEnum):
    COM = 1
    IP = 2


class Settings(BaseModel):
    # Производитель, чтобы сервер понимал какой драйвер использовать
    manufacture: Manufacture = Field(default=Manufacture.ATOL)

    # Общие настройки
    lib_path: str = Field(default="")  # Путь к драйверу
    conn_type: ConnectionType = Field(default=ConnectionType.COM)  # Тип подключения

    ip_address: str = Field(default="192.168.1.10")
    ip_port: int = Field(default=5555)
    com_file: int = Field(default=1)

    def load_settings(self, file_name: str = "config.json"):
        # Загрузка конфигурации из файла
        # Получаем текущий рабочий каталог

        try:
            with open(file_name, "r") as f:
                new_settings = Settings(**json.load(f))
                self.__dict__.update(new_settings.model_dump())

        except FileNotFoundError:
            return

    def save_settings(self, file_name: str = "config.json"):
        # Сохранение конфигурации
        with open(file_name, "w") as f:
            json.dump(self.model_dump(by_alias=True), f)


if __name__ == "__main__":
    sets = Settings()
    sets.load_settings()
