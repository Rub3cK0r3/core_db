# Son fundamentales en FastAPI para validar solicitudes/respuestas, garantizando la integridad de los datos y generando esquemas JSON.

from typing import Dict, Optional
from pydantic import BaseModel

class EventResponse(BaseModel):
    id: str
    severity: str
    stack: Optional[str] = None
    type: Optional[str] = None
    timestamp: int
    received_at: int
    resource: Optional[str] = None
    referrer: Optional[str] = None
    app_name: str
    app_version: Optional[str] = None
    app_stage: Optional[str] = None
    tags: Optional[Dict] = None
    endpoint_id: str
    endpoint_language: Optional[str] = None
    endpoint_platform: Optional[str] = None
    endpoint_os: Optional[str] = None
    endpoint_os_version: Optional[str] = None
    endpoint_runtime: Optional[str] = None
    endpoint_runtime_version: Optional[str] = None
    endpoint_country: Optional[str] = None
    endpoint_user_agent: Optional[str] = None
    endpoint_device_type: Optional[str] = None

    model_config = {
        "from_attributes": True  # reemplaza orm_mode
    }

class EventCreate(BaseModel):
    severity: str
    stack: Optional[str] = None
    type: Optional[str] = None
    timestamp: int
    resource: Optional[str] = None
    referrer: Optional[str] = None
    app_name: str
    app_version: Optional[str] = None
    app_stage: Optional[str] = None
    tags: Optional[Dict] = None
    endpoint_id: str
    endpoint_language: Optional[str] = None
    endpoint_platform: Optional[str] = None
    endpoint_os: Optional[str] = None
    endpoint_os_version: Optional[str] = None
    endpoint_runtime: Optional[str] = None
    endpoint_runtime_version: Optional[str] = None
    endpoint_country: Optional[str] = None
    endpoint_user_agent: Optional[str] = None
    endpoint_device_type: Optional[str] = None
