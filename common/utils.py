import logging
from typing import get_type_hints

from common.enums import DeviceAction


logger = logging.getLogger(__name__)


def create_model(klass, src):
    src_dict = vars(src)

    attrs = get_type_hints(klass)
    kwargs = {k: v for k, v in src_dict.items() if k in attrs}

    try:
        return klass(**kwargs)
    except Exception:
        logger.exception(
            f"Failed to create instance of {klass} from {src} with {kwargs=} {attrs=} {src_dict=}"
        )


def common_kwargs(klass, src: dict, exclude=[]):
    kwargs = {
        k: v
        for k, v in src.items()
        if k not in exclude and k in getattr(klass, "__annotations__", {})
    }
    return kwargs


def copy_attrs(src, dst, exclude=[]):
    for attr in dir(src):
        # skip private / dunder attributes
        if attr.startswith("_") or attr in exclude:
            continue

        # skip methods / callables
        value = getattr(src, attr)
        if callable(value):
            continue

        # only copy if dst has the attribute
        if hasattr(dst, attr):
            setattr(dst, attr, value)


def to_supported_actions(*args: list[DeviceAction]):
    return ",".join([a.name for a in args])


def to_device_actions(supported_actions: str) -> list[DeviceAction]:
    actions = []
    for action in supported_actions.split(","):
        actions.append(DeviceAction(action))
    return actions
