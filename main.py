import os
import sys
import json
import time

from server.schemas.settings import ConnectionType, Manufacture
from io import StringIO

# for exe correct path
if getattr(sys, 'frozen', False):
    current_dir = os.path.join(os.path.dirname(sys.executable), '_internal')
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))

parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

settings_dir = os.getenv('APPDATA')

from server.models.atol_device import AtolCashRegistr
from server.models.base import CashRegistr

from PyQt6.QtWidgets import QApplication, QWidget, QComboBox, QVBoxLayout, QLineEdit, QPushButton, QSystemTrayIcon, \
    QFormLayout, QFileDialog, QHBoxLayout, QMenu
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QIntValidator, QIcon, QAction
import serial.tools.list_ports

from uvicorn import Config

from mock import manufactures, connection_types
from server.uvicorn_server import UvicornServer
import multiprocessing

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Утилита для взаимодействия с кассой")

        if not os.path.exists(settings_dir.replace(os.sep, '/') + '/config.json'):
            device = {
                "manufacture": 1,
                "lib_path": current_dir.replace(os.sep, '/') + "/fptr10.dll",
                "conn_type": 2,
                "com_file": 3,
                "ip_address": "",
                "ip_port": 5555
            }
            self.save_to_json(data=device)

        self.config = Config('main:app', port=8001, log_level='warning')
        self.server = UvicornServer(config=self.config)

        # Создаем иконку для трея
        self.tray_icon = QSystemTrayIcon(QIcon(current_dir + '/1.png'), self)
        self.tray_icon.setToolTip("Приложение свернуто в трей")
        self.tray_icon.show()

        self.tray_icon.activated.connect(self.tray_icon_activated)
        # Создаем контекстное меню для иконки в трее
        self.tray_menu = QMenu(self)

        # Добавляем действия (кнопки) в контекстное меню
        self.start_server_action = QAction("Запустить сервер", self)
        self.start_server_action.triggered.connect(self.connect_device)
        self.tray_menu.addAction(self.start_server_action)

        self.stop_server_action = QAction("Остановить сервер", self)
        self.stop_server_action.triggered.connect(self.stop_server)
        self.tray_menu.addAction(self.stop_server_action)

        self.restart_server_action = QAction("Перезапустить сервер", self)
        self.restart_server_action.triggered.connect(self.restart_server)
        self.tray_menu.addAction(self.restart_server_action)

        self.show_window_application = QAction("Показать окно приложения", self)
        self.show_window_application.triggered.connect(self.show)
        self.tray_menu.addAction(self.show_window_application)

        self.close_application = QAction("Закрыть приложение", self)
        self.close_application.triggered.connect(self.close_app)
        self.tray_menu.addAction(self.close_application)

        # Устанавливаем контекстное меню для иконки в трее
        self.tray_icon.setContextMenu(self.tray_menu)

        layout = QVBoxLayout()

        # Создаем форму для отображения COM портов, IP адреса и порта
        form_layout = QFormLayout()

        # Создаем выпадающий список для выбора типа устройства
        self.manufacture_device = QComboBox()
        form_layout.addRow("Производитель устройства:", self.manufacture_device)

        # # Создаем горизонтальное компоновочное расположение для поля ввода и кнопки выбора файла
        # file_layout = QHBoxLayout()

        # # Поле для ввода пути к файлу
        # self.file_path_input = QLineEdit()
        # self.file_path_input.setPlaceholderText("Выберите файл")
        # file_layout.addWidget(self.file_path_input)

        # # Кнопка для выбора файла
        # self.select_file_button = QPushButton("Выбрать файл")
        # self.select_file_button.clicked.connect(self.select_file)
        # file_layout.addWidget(self.select_file_button)

        # # Добавляем компоновочное расположение в основное компоновочное расположение формы
        # form_layout.addRow("Путь к файлу:", file_layout)

        # Создаем выпадающий список для выбора типа подключения
        self.type_connection = QComboBox()
        form_layout.addRow("Тип подключения:", self.type_connection)

        # Создаем выпадающий список для отображения COM-портов
        self.combo_box_ports = QComboBox()
        form_layout.addRow("COM порт:", self.combo_box_ports)

        # Создаем поле ввода для IP-адреса
        self.ip_address = QLineEdit()
        self.ip_address.setPlaceholderText("Введите IP адрес")
        self.ip_address.setInputMask("000.000.000.000;_")  # Устанавливаем маску для IP адреса
        form_layout.addRow("IP адрес:", self.ip_address)

        # Создаем поле ввода для порта
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Введите порт")
        self.port_input.setValidator(QIntValidator())  # Устанавливаем валидатор для порта (только цифры)
        form_layout.addRow("Порт:", self.port_input)

        layout.addLayout(form_layout)

        # Создаем кнопку для подключения
        self.start_server_button = QPushButton("Запустить сервер")
        self.start_server_button.clicked.connect(self.connect_device)
        layout.addWidget(self.start_server_button)

        # Создаем кнопку для подключения
        self.reset_settings = QPushButton("Перезаписать настройки")
        self.reset_settings.clicked.connect(self.reset_settings_json)
        layout.addWidget(self.reset_settings)

        # Создаем кнопку для подключения
        self.stop_server_button = QPushButton("Остановить сервер")
        self.stop_server_button.clicked.connect(self.stop_server)
        layout.addWidget(self.stop_server_button)

        # Создаем кнопку для подключения
        self.reset_server_button = QPushButton("Перезапустить сервер")
        self.reset_server_button.clicked.connect(self.restart_server)
        layout.addWidget(self.reset_server_button)

        # вызываем метод для обновления состояния кнопки
        self.update_start_server_button()

        # Заполняем списоки
        self.populate_ports()
        self.populate_manufacture()
        self.type_connection_list()

        self.setLayout(layout)

        self.load_from_json()

    def load_from_json(self):
        try:
            with open(settings_dir.replace(os.sep, '/') + "/config.json", "r") as json_file:
                data = json.load(json_file)
                self.manufacture_device.setCurrentIndex(self.manufacture_device.findData(data["manufacture"]))
                # self.file_path_input.setText(data["lib_path"])
                self.type_connection.setCurrentIndex(self.type_connection.findData(data["conn_type"]))
                ports = serial.tools.list_ports.comports()
                list_ports = {port.device: port.description for port in ports}
                for item in list_ports:
                    if f"COM{data["com_file"]}" in item:
                        self.combo_box_ports.setCurrentText(list_ports.get(item))
                self.ip_address.setText(data["ip_address"])
                self.port_input.setText(str(data["ip_port"]))
                self.server
        except Exception as e:
            print("Ошибка при загрузке данных из JSON файла:", e)

    def close_app(self):
        # Остановка сервера перед закрытием приложения (если он запущен)
        if self.server.status():
            self.server.stop()
        # Закрываем приложение
        QCoreApplication.quit()

    def closeEvent(self, event):
        # Отменяем закрытие окна
        event.ignore()
        # Сворачиваем окно в трей
        self.hide_to_tray()

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()  # Показываем окно приложения

    def select_file(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            self.file_path_input.setText(selected_file)

    def populate_ports(self):
        # Получаем список доступных COM-портов
        ports = serial.tools.list_ports.comports()
        # Добавляем COM-порты в выпадающий список
        for port in ports:
            self.combo_box_ports.addItem(port.description, port.device)

    def populate_manufacture(self):
        # Добавляем COM-порты в выпадающий список
        for manufacture in Manufacture:
            self.manufacture_device.addItem(manufacture.name, manufacture.value)

    def type_connection_list(self):
        # Добавляем COM-порты в выпадающий список
        for connection_type in ConnectionType:
            self.type_connection.addItem(connection_type.name, connection_type.value)

    def reset_settings_json(self):
        selected_ip = self.ip_address.text()
        selected_port = self.port_input.text()
        selected_com_port = self.combo_box_ports.currentData()
        manufacture_device = self.manufacture_device.currentData()
        type_connection = self.type_connection.currentData()

        # Создаем словарь с введенными данными
        device = {
            "manufacture": manufacture_device,
            "conn_type": type_connection,
            "com_file": int(selected_com_port[3:4]) if selected_com_port is not None else None,
            "ip_address": selected_ip or None,
            "ip_port": int(selected_port) or None,
        }
        # Сохраняем данные в JSON файл
        self.save_to_json(device)

    def restart_server(self):
        self.server.stop()
        self.server.start()

    def connect_device(self):
        self.server.start()
        self.update_start_server_button()  # обновляем состояние кнопки

    def stop_server(self):
        self.server.stop()
        self.update_start_server_button()  # обновляем состояние кнопки

    def hide_to_tray(self):
        self.hide()

    def update_start_server_button(self):
        # Если сервер запущен, делаем кнопку "Запустить сервер" неактивной, а остальные активными
        if self.server.status():
            self.start_server_button.setEnabled(False)
            self.stop_server_button.setEnabled(True)
            self.reset_server_button.setEnabled(True)
            self.tray_icon.setIcon(QIcon(current_dir + '/4.png'))
            self.start_server_action.setEnabled(False)
            self.stop_server_action.setEnabled(True)
            self.restart_server_action.setEnabled(True)
        else:
            self.start_server_button.setEnabled(True)
            self.stop_server_button.setEnabled(False)
            self.reset_server_button.setEnabled(False)
            self.tray_icon.setIcon(QIcon(current_dir + '/3.png'))
            self.start_server_action.setEnabled(True)
            self.stop_server_action.setEnabled(False)
            self.restart_server_action.setEnabled(False)

    def save_to_json(self, data: {}):
        try:
            with open(settings_dir.replace(os.sep, '/') + "/config.json", "w") as json_file:
                json.dump(data, json_file, indent=4, ensure_ascii=False)
            print("Данные успешно сохранены в файл 'config.json'")
        except Exception as e:
            print("Ошибка при сохранении данных в JSON файл:", e)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    sys.stdout = StringIO() # hide console for launch app        
    app1 = QApplication(sys.argv)
    app1.setWindowIcon(QIcon(current_dir + '/1.png'))
    window = MainWindow()
    window.show()

    sys.exit(app1.exec())
