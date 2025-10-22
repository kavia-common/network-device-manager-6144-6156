"""Marshmallow schemas for request/response validation."""

from datetime import datetime
from marshmallow import Schema, fields, validates, ValidationError, validate

DEVICE_TYPES = ("router", "switch", "server")
STATUS_TYPES = ("online", "offline")

class DeviceBaseSchema(Schema):
    name = fields.String(required=True, description="Device name")
    ip_address = fields.String(required=True, description="IPv4/IPv6 address")
    type = fields.String(required=True, validate=validate.OneOf(DEVICE_TYPES), description="Device type")
    location = fields.String(required=False, allow_none=True, description="Physical or logical location")
    status = fields.String(required=False, validate=validate.OneOf(STATUS_TYPES), missing="offline", description="Device status")
    notes = fields.String(required=False, allow_none=True, description="Additional notes")

class DeviceCreateSchema(DeviceBaseSchema):
    pass

class DeviceUpdateSchema(Schema):
    name = fields.String(required=False)
    ip_address = fields.String(required=False)
    type = fields.String(required=False, validate=validate.OneOf(DEVICE_TYPES))
    location = fields.String(required=False, allow_none=True)
    status = fields.String(required=False, validate=validate.OneOf(STATUS_TYPES))
    notes = fields.String(required=False, allow_none=True)

class DeviceResponseSchema(DeviceBaseSchema):
    id = fields.String(required=True, description="Device ID")
    created_at = fields.DateTime(required=True, description="Created timestamp (UTC)")
    updated_at = fields.DateTime(required=True, description="Updated timestamp (UTC)")
