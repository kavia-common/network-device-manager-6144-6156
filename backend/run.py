import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "3001"))
    # host 0.0.0.0 for container friendliness
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_ENV") == "development")
