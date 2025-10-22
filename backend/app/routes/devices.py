"""Devices API endpoints providing CRUD and ping functionality.

Routes are registered under API_PREFIX + /devices.
"""

from datetime import datetime, timezone
from bson import ObjectId
from flask import current_app, request
from flask_smorest import Blueprint, abort
from flask.views import MethodView

from ..db import get_devices_collection
from ..schemas import DeviceCreateSchema, DeviceUpdateSchema, DeviceResponseSchema
from ..utils.ping import ping_host

blp = Blueprint(
    "Devices",
    "devices",
    url_prefix="",
    description="CRUD and ping endpoints for network devices",
)

def _serialize_device(doc) -> dict:
    """Map MongoDB document to API response dict."""
    return {
        "id": str(doc.get("_id")),
        "name": doc.get("name"),
        "ip_address": doc.get("ip_address"),
        "type": doc.get("type"),
        "location": doc.get("location"),
        "status": doc.get("status", "offline"),
        "notes": doc.get("notes"),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }

def _now():
    return datetime.now(timezone.utc)

@blp.route("/")
class DevicesList(MethodView):
    @blp.response(200, DeviceResponseSchema(many=True), description="List all devices")
    def get(self):
        """List devices.

        Returns:
            list[DeviceResponse]: All devices.
        """
        coll = get_devices_collection()
        docs = list(coll.find().sort("created_at", 1))
        return [_serialize_device(d) for d in docs]

    @blp.arguments(DeviceCreateSchema)
    @blp.response(201, DeviceResponseSchema, description="Create a device")
    def post(self, payload):
        """Create a device with validation."""
        coll = get_devices_collection()
        now = _now()
        doc = {
            "name": payload["name"],
            "ip_address": payload["ip_address"],
            "type": payload["type"],
            "location": payload.get("location"),
            "status": payload.get("status", "offline"),
            "notes": payload.get("notes"),
            "created_at": now,
            "updated_at": now,
        }
        res = coll.insert_one(doc)
        created = coll.find_one({"_id": res.inserted_id})
        return _serialize_device(created)

@blp.route("/<string:device_id>")
class DeviceDetail(MethodView):
    @blp.response(200, DeviceResponseSchema, description="Get device by ID")
    def get(self, device_id):
        """Get a device by ID."""
        coll = get_devices_collection()
        try:
            oid = ObjectId(device_id)
        except Exception:
            abort(400, message="Invalid device id")
        doc = coll.find_one({"_id": oid})
        if not doc:
            abort(404, message="Device not found")
        return _serialize_device(doc)

    @blp.arguments(DeviceUpdateSchema)
    @blp.response(200, DeviceResponseSchema, description="Updated device")
    def put(self, payload, device_id):
        """Update a device by ID."""
        coll = get_devices_collection()
        try:
            oid = ObjectId(device_id)
        except Exception:
            abort(400, message="Invalid device id")
        update_fields = {k: v for k, v in payload.items()}
        if not update_fields:
            abort(400, message="No fields to update")
        update_fields["updated_at"] = _now()
        res = coll.find_one_and_update(
            {"_id": oid},
            {"$set": update_fields},
            return_document=True,
        )
        if not res:
            abort(404, message="Device not found")
        # Some pymongo versions return dict when return_document=True isn't set; ensure we fetch
        doc = coll.find_one({"_id": oid})
        return _serialize_device(doc)

    @blp.response(204, description="Device deleted")
    def delete(self, device_id):
        """Delete a device by ID."""
        coll = get_devices_collection()
        try:
            oid = ObjectId(device_id)
        except Exception:
            abort(400, message="Invalid device id")
        res = coll.delete_one({"_id": oid})
        if res.deleted_count == 0:
            abort(404, message="Device not found")
        return "", 204

@blp.route("/<string:device_id>/ping")
class DevicePing(MethodView):
    @blp.response(200, DeviceResponseSchema, description="Ping device and update status when enabled")
    def post(self, device_id):
        """Ping device by ID and update its status when ENABLE_PING=true.

        Returns:
            DeviceResponse: The updated (or unchanged) device document.
        """
        coll = get_devices_collection()
        try:
            oid = ObjectId(device_id)
        except Exception:
            abort(400, message="Invalid device id")
        doc = coll.find_one({"_id": oid})
        if not doc:
            abort(404, message="Device not found")

        if not current_app.config.get("ENABLE_PING", True):
            # Return device unchanged and a header or message indicating disabled
            # Using response body message per acceptance criteria
            # We include the device data with status as-is
            # flask-smorest requires schema, so return device as schema plus X-Note via headers is not ideal
            result = _serialize_device(doc)
            # Append visible note in "notes" while not mutating DB
            result["notes"] = (result.get("notes") or "")
            return result, 200, {"X-Ping-Note": "Ping disabled by configuration"}

        reachable = ping_host(doc.get("ip_address"))
        new_status = "online" if reachable else "offline"
        coll.update_one({"_id": oid}, {"$set": {"status": new_status, "updated_at": _now()}})
        updated = coll.find_one({"_id": oid})
        return _serialize_device(updated)
