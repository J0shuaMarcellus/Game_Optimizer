import ctypes
import logging
import os
import socket
import sys
import threading
import time
import webbrowser

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8080
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"
SERVER_WAIT_TIMEOUT = 12.0


def get_log_path():
    if getattr(sys, "_MEIPASS", False):
        return os.path.join(os.path.dirname(sys.executable), "error_log.txt")
    return "error_log.txt"


logging.basicConfig(
    filename=get_log_path(),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("game_optimizer")


def get_base_path():
    if getattr(sys, "_MEIPASS", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def show_error_dialog(message):
    try:
        ctypes.windll.user32.MessageBoxW(None, message, "Game Optimizer", 0x10)
    except Exception:
        logger.exception("Could not show Windows error dialog.")


def start_server(server_state):
    try:
        base_path = get_base_path()
        os.chdir(base_path)
        logger.info("Starting Flask server from %s", base_path)

        from step2_server import app
        import logging as flask_log

        flask_log.getLogger("werkzeug").setLevel(flask_log.ERROR)
        app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False, use_reloader=False)
    except Exception as exc:
        server_state["error"] = exc
        logger.exception("Flask server failed to start.")


def wait_for_server(timeout_seconds):
    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        try:
            with socket.create_connection((SERVER_HOST, SERVER_PORT), timeout=0.5):
                logger.info("Server is reachable at %s", SERVER_URL)
                return True
        except OSError:
            time.sleep(0.2)

    logger.error("Server did not become reachable within %.1f seconds.", timeout_seconds)
    return False


def open_in_browser():
    logger.info("Falling back to browser at %s", SERVER_URL)
    opened = webbrowser.open(SERVER_URL)
    if not opened:
        logger.error("Browser fallback failed to open %s", SERVER_URL)
        show_error_dialog(
            "Game Optimizer could not open the app window or your browser.\n"
            f"Check {get_log_path()} for details."
        )
        return

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Browser fallback interrupted by user.")


if __name__ == "__main__":
    logger.info("Game Optimizer launch started.")

    server_state = {"error": None}
    server_thread = threading.Thread(
        target=start_server,
        args=(server_state,),
        daemon=True,
        name="game-optimizer-server",
    )
    server_thread.start()

    server_ready = wait_for_server(SERVER_WAIT_TIMEOUT)
    if not server_ready:
        if server_state["error"] is not None:
            show_error_dialog(
                "Game Optimizer could not start its local server.\n"
                f"Check {get_log_path()} for details."
            )
        else:
            show_error_dialog(
                "Game Optimizer timed out while starting its local server.\n"
                f"Check {get_log_path()} for details."
            )
        sys.exit(1)

    try:
        logger.info("Creating desktop window.")
        import webview

        webview.create_window(
            "Game Optimizer",
            url=SERVER_URL,
            width=1100,
            height=750,
            resizable=True,
            min_size=(800, 500),
        )

        logger.info("Starting desktop window event loop.")
        webview.start()
    except Exception:
        logger.exception("Desktop window failed. Trying browser fallback.")
        open_in_browser()
