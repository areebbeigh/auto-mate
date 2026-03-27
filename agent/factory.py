from common.service.mqtt import get_mqtt_service_ctx
from agent.tuya_agent import TinyTuyaAgent
from agent.tapo_agent import TapoAgent

AGENT_CLASSES = [
    TinyTuyaAgent, TapoAgent
]
        
