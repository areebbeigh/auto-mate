from common.service.mqtt import MQTTService
from agent.tuya_agent import TinyTuyaAgent
from agent.tapo_agent import TapoAgent

AGENT_CLASSES = [
    TinyTuyaAgent, TapoAgent
]

def get_agents(mqtt: MQTTService):
    agents = []
    for klass in AGENT_CLASSES:
        agent = klass(name=klass.__name__, mqtt_service=mqtt)
        agents.append(agent)
    return agents
        
