from enum import Enum


class IntegrationType(Enum):
    TINYTUYA = "TINYTUYA"
    TAPO = "TAPO"


class DeviceAction(Enum):
    TOGGLE_ON_OFF = "TOGGLE_ON_OFF"
    SET_COLOR = "SET_COLOR"
