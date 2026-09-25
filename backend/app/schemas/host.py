"""Discovered host/port/service response schemas."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class PortServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    host_id: uuid.UUID
    port_number: int
    protocol: str
    state: str
    service_name: Optional[str]
    product: Optional[str]
    version: Optional[str]
    extra_info: Optional[str]
    created_at: datetime


class HostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    scan_id: uuid.UUID
    ip_address: str
    hostname: Optional[str]
    status: str
    os_name: Optional[str]
    os_accuracy: Optional[int]
    mac_address: Optional[str]
    created_at: datetime
    port_services: List[PortServiceResponse] = []