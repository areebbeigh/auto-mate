from common.config import Settings as CommonSettings


class Settings(CommonSettings):
    TINY_TUYA_CONIFG = CommonSettings.CONFIG_DIR / "tiny_tuya.json"

settings = Settings()
