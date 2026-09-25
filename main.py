from app import app
import os
import threading
import webbrowser


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))

    # Opens the dashboard for a simple one-command local experience.
    # Set OPEN_BROWSER=false if you need to start without a browser window.
    if os.environ.get("OPEN_BROWSER", "true").lower() == "true":
        threading.Timer(1, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()

    app.run(
        debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true",
        host="127.0.0.1",
        port=port,
    )
