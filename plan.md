# auto-mate

Initial plan for my home IOT framework.

# Services

1. FastAPI server: Dashboards, user control, database, reporting/notifications, apis
2. MQTT: Decoupling layer - Standardized RPCs
3. Bridges/Services: OEM specific integration
    - Status polling
    - Actions
    - Device discovery
4. Scheduler: Automation/scheduling
5. Monitoring: Optional monitoring and alarms

# Setup Steps

1. Configure integrations (e.g tapo credentials, tinytuya keys)
2. Continuous device discovery calls
3. Initiate device connections (credentials)
4. Poll and report device stats

# Schema

User
    id
    email
    password

Integration
    id
    type (TINYTUYA/TAPO)
    access_key
    access_key_secret
    username
    password

Device
    id
    controllable: bool
    name
    last_known_ip
    payload

Schedule

Alerts

Notifications
