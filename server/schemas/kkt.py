from dataclasses import Field
from enum import IntEnum
from typing import Any

from pydantic import BaseModel


class OperationError(BaseModel):
    code: int
    description: str


class JsonTaskResponse(BaseModel):
    request: dict[str, Any]
    result: dict[str, Any] | str


class MethodError(BaseModel):
    error: OperationError


class DeviceConnStatus(IntEnum):
    ACTIVE = 1
    DISABLE = 0
