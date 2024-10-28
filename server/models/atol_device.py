import json

from pydantic import AliasChoices, BaseModel, Field

import sys
import os

# Add the directory containing the 'models' module to the Python path
# for exe correct path
if getattr(sys, 'frozen', False):
    current_dir = os.path.join(os.path.dirname(sys.executable), '_internal')
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.dirname(current_dir)

parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)


from server.drivers.atol10 import IFptr
from server.models.base import CashRegistr, DeviceManufactureType
from server.schemas.kkt import OperationError
from server.schemas.settings import ConnectionType, Settings


class AtolSettings(BaseModel):

    # LIBFPTR_SETTING_LIBRARY_PATH = "LibraryPath"
    lib_path: str = Field(
        validation_alias=AliasChoices("lib_path", IFptr.LIBFPTR_SETTING_LIBRARY_PATH),
        serialization_alias=IFptr.LIBFPTR_SETTING_LIBRARY_PATH,
        default="",
    )

    # LIBFPTR_SETTING_MODEL = "Model"
    device_model: int = Field(
        validation_alias=AliasChoices("device_model", IFptr.LIBFPTR_SETTING_MODEL),
        serialization_alias=IFptr.LIBFPTR_SETTING_MODEL,
        default=500,
    )

    # LIBFPTR_SETTING_PORT = "Port"
    conn_type: ConnectionType = Field(
        validation_alias=AliasChoices("conn_type", IFptr.LIBFPTR_SETTING_PORT),
        serialization_alias=IFptr.LIBFPTR_SETTING_PORT,
        default=ConnectionType.COM,
    )

    # LIBFPTR_SETTING_BAUDRATE = "BaudRate"

    # LIBFPTR_SETTING_BITS = "Bits"

    # LIBFPTR_SETTING_PARITY = "Parity"

    # LIBFPTR_SETTING_STOPBITS = "StopBits"

    # LIBFPTR_SETTING_IPADDRESS = "IPAddress"
    ip_address: str = Field(
        validation_alias=AliasChoices("ip_address", IFptr.LIBFPTR_SETTING_IPADDRESS),
        serialization_alias=IFptr.LIBFPTR_SETTING_IPADDRESS,
        default="192.168.1.10",
    )

    # LIBFPTR_SETTING_IPPORT = "IPPort"
    ip_port: int = Field(
        validation_alias=AliasChoices("ip_port", IFptr.LIBFPTR_SETTING_IPPORT),
        serialization_alias=IFptr.LIBFPTR_SETTING_IPPORT,
        default=5555,
    )

    # LIBFPTR_SETTING_MACADDRESS = "MACAddress"

    # LIBFPTR_SETTING_COM_FILE = "ComFile"
    com_file: int = Field(
        validation_alias=AliasChoices("com_file", IFptr.LIBFPTR_SETTING_COM_FILE),
        serialization_alias=IFptr.LIBFPTR_SETTING_COM_FILE,
        default=1,
    )

    # LIBFPTR_SETTING_USB_DEVICE_PATH = "UsbDevicePath"

    # LIBFPTR_SETTING_BT_AUTOENABLE = "AutoEnableBluetooth"

    # LIBFPTR_SETTING_BT_AUTODISABLE = "AutoDisableBluetooth"

    # LIBFPTR_SETTING_ACCESS_PASSWORD = "AccessPassword"

    # LIBFPTR_SETTING_USER_PASSWORD = "UserPassword"

    # LIBFPTR_SETTING_OFD_CHANNEL = "OfdChannel"

    # LIBFPTR_SETTING_EXISTED_COM_FILES = "ExistedComFiles"

    # LIBFPTR_SETTING_SCRIPTS_PATH = "ScriptsPath"

    # LIBFPTR_SETTING_DOCUMENTS_JOURNAL_PATH = "DocumentsJournalPath"

    # LIBFPTR_SETTING_USE_DOCUMENTS_JOURNAL = "UseDocumentsJournal"

    # LIBFPTR_SETTING_AUTO_RECONNECT = "AutoReconnect"

    # LIBFPTR_SETTING_INVERT_CASH_DRAWER_STATUS = "InvertCashDrawerStatus"

    # LIBFPTR_SETTING_REMOTE_SERVER_ADDR = "RemoteServerAddr"

    # LIBFPTR_SETTING_REMOTE_SERVER_CONNECTION_TIMEOUT = "RemoteServerConnectionTimeout"

    # LIBFPTR_SETTING_VALIDATE_MARK_WITH_FNM_ONLY = "ValidateMarksWithFnmOnly"

    # LIBFPTR_SETTING_AUTO_MEASUREMENT_UNIT = "AutoMeasurementUnit"

    # LIBFPTR_SETTING_SILENT_REBOOT = "SilentReboot"


class AtolCashRegistr(CashRegistr):

    def __init__(self, id: str, settings: Settings):
        super().__init__(id, manufacture=DeviceManufactureType.ATOL)

        self.fptr = IFptr(settings.lib_path, self.id)
        self.settings = AtolSettings(**settings.model_dump())
        self.set_driver_settings(self.settings.model_dump(by_alias=True))

    def error(self):

        return OperationError(
            code=self.fptr.errorCode(), description=self.fptr.errorDescription()
        ).model_dump()

    def driver_settings(self) -> AtolSettings:

        return AtolSettings(**self.fptr.getSettings())

    def set_driver_settings(self, settings: str):

        return self.fptr.setSettings(settings)

    def activate(self):

        return self.fptr.open()

    def deactivate(self):

        return self.fptr.close()

    def conn_status(self) -> bool:

        return self.fptr.isOpened()

    # Очередь заданий
    def create_request(self, task: str) -> tuple[bool, dict]:
        self.fptr.setParam(IFptr.LIBFPTR_PARAM_JSON_DATA, task)  # Записываем задание

        process_result = self.fptr.processJson()
        if process_result != 0:
            return False, self.error()

        return True, json.loads(self.fptr.getParamString(IFptr.LIBFPTR_PARAM_JSON_DATA))

    def status_request(self):
        pass

    def delete_request(self):
        pass

    def status_requests_query(self):
        pass

    # Информация

    def shift_status(self):
        pass

    def shift_totals(self):
        pass

    def income_totals(self):
        pass

    def outcome_totals(self):
        pass

    def receipt_totals(self):
        pass

    def fn_info(self):
        pass

    def fn_status(self):
        pass

    def ofd_status(self):
        pass

    def ism_status(self):
        pass

    def licenses(self):
        pass

    def device_settings(self):
        pass
