from abc import ABC, abstractmethod


class DeviceType:
    UNDEFINED = 0
    CASH_REGISTR = 1


class DeviceManufactureType:
    UNDEFINED = 0
    ATOL = 1


class Device(ABC):

    @abstractmethod
    def __init__(self, id: str, type: DeviceType):
        self.__id = id
        self.__type = type

    @property
    def id(self):
        return self.__id

    @property
    def type(self):
        return self.__type

    # @abstractmethod
    # def device_info(self):
    #     pass

    # @abstractmethod
    # def device_status(self):
    #     pass


class CashRegistr(Device):

    @abstractmethod
    def __init__(self, id: str, manufacture: DeviceManufactureType):
        super().__init__(id, DeviceType.CASH_REGISTR)
        self.__manufacture = manufacture

    @property
    def manufacture(self):
        return self.__manufacture

    @abstractmethod
    def error(self):
        pass

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def deactivate(self):
        pass

    @abstractmethod
    def conn_status(self):
        pass

    # Очередь заданий
    @abstractmethod
    def create_request(self):
        pass

    @abstractmethod
    def status_request(self):
        pass

    @abstractmethod
    def delete_request(self):
        pass

    @abstractmethod
    def status_requests_query(self):
        pass

    # Информация
    @abstractmethod
    def shift_status(self):
        pass

    @abstractmethod
    def shift_totals(self):
        pass

    @abstractmethod
    def income_totals(self):
        pass

    @abstractmethod
    def outcome_totals(self):
        pass

    @abstractmethod
    def receipt_totals(self):
        pass

    @abstractmethod
    def fn_info(self):
        pass

    @abstractmethod
    def fn_status(self):
        pass

    @abstractmethod
    def ofd_status(self):
        pass

    @abstractmethod
    def ism_status(self):
        pass

    @abstractmethod
    def licenses(self):
        pass

    @abstractmethod
    def device_settings(self):
        pass
