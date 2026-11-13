"""Envelope of a telemetry batch.

The field set is the Phase 1 contract. Property allowlists are checked by the
frontend tests against event-schemas.json. This stub checks the envelope so a
later phase can reuse the same model.
"""

from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

EventType = Literal[
    "inbound_order_created",
    "outbound_order_created",
    "stock_threshold_triggered",
    "direct_stock_edit_rejected",
    "kit_cost_variance_detected",
    "login_failed",
    "login_succeeded",
    "session_expired",
    "credential_rejected",
    "password_reset_requested",
    "api_latency_recorded",
    "page_load_recorded",
    "frontend_exception_recorded",
    "api_response_failed",
    "section_viewed",
    "flow_abandoned",
    "order_validation_failed",
    "asset_created",
    "catalogue_gap_recorded",
    "web_vital_recorded",
]

_PATHS = Literal[
    "/",
    "/login",
    "/register",
    "/forgot-password",
    "/reset-password",
    "/proveedores",
    "/account/profile",
    "/account/change-password",
    "/backoffice/inventory/products",
    "/backoffice/inventory/orders",
    "/backoffice/inventory/orders/inbound",
    "/backoffice/inventory/orders/outbound",
]


class WebVitalProperties(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: Literal["backoffice", "portal"]
    path_template: _PATHS
    metric_name: Literal["LCP", "INP", "CLS", "FCP", "TTFB"]
    value: float = Field(ge=0, le=600_000)
    rating: Literal["good", "needs-improvement", "poor"]

_UUID = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
_TIMESTAMP = (
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)


class TelemetryEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    eventId: str = Field(pattern=_UUID)
    timestamp: str = Field(pattern=_TIMESTAMP)
    sessionId: str = Field(pattern=rf"^(missing|{_UUID[1:-1]})$")
    userId: str = Field(pattern=rf"^(anonymous|{_UUID[1:-1]})$")
    event_type: EventType
    schemaVersion: Literal["1.0.0", "1.1.0"]
    requestId: str = Field(pattern=_UUID)
    properties: dict[str, Any]

    @model_validator(mode="after")
    def web_vital_uses_the_minor_schema(self) -> Self:
        if self.event_type != "web_vital_recorded":
            return self
        if self.schemaVersion != "1.1.0":
            raise ValueError("web_vital_recorded usa schemaVersion 1.1.0")
        WebVitalProperties.model_validate(self.properties)
        return self


class TelemetryBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    events: list[TelemetryEvent]
