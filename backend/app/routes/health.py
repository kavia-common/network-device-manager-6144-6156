from flask_smorest import Blueprint
from flask.views import MethodView

# Health check blueprint — intentionally at root "/"
blp = Blueprint("Healt Check", "health check", url_prefix="/", description="Health check route")

@blp.route("/")
class HealthCheck(MethodView):
    # PUBLIC_INTERFACE
    def get(self):
        """Health check endpoint.

        Returns:
            dict: {"message": "Healthy"} to indicate service is up.
        """
        return {"message": "Healthy"}
