"""Keeps a free Render service awake by asking for its own public /health address every 10 minutes.

Render puts a free web service to sleep after 15 minutes without inbound traffic. A request to the
service's PUBLIC address counts as inbound traffic, so it must go out to the internet and back in:
a request to localhost would not count.

Call start_keep_alive() once, where the Flask app is created. It does nothing on your own computer,
because the address comes from RENDER_EXTERNAL_URL, which Render sets on every web service.

Settings (all optional):
    KEEP_ALIVE=off                       turn it off without changing code
    KEEP_ALIVE_URL=https://your.domain   use this address instead (for example, a custom domain)
    KEEP_ALIVE_INTERVAL_SECONDS=600      how often to ping; must stay under 900 (15 minutes)
"""
import logging
import os
import threading
import time
import urllib.request

INTERVAL_SECONDS = 10 * 60
_started = False


def _ping(url):
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            logging.info("keep-alive: %s answered %s", url, response.status)
    except Exception as err:   # a failed ping must never stop the app
        logging.warning("keep-alive: ping to %s failed: %s", url, err)


def start_keep_alive():
    """Starts the background pinger. Returns True if it started."""
    global _started
    if _started:
        return False
    if os.environ.get("KEEP_ALIVE", "on").strip().lower() in ("off", "0", "false"):
        return False

    base = os.environ.get("KEEP_ALIVE_URL") or os.environ.get("RENDER_EXTERNAL_URL")
    if not base:
        return False   # not running on Render, so there is nothing to keep awake

    interval = float(os.environ.get("KEEP_ALIVE_INTERVAL_SECONDS") or INTERVAL_SECONDS)
    url = base.rstrip("/") + "/health"

    def loop():
        while True:
            time.sleep(interval)
            _ping(url)

    threading.Thread(target=loop, name="keep-alive", daemon=True).start()
    _started = True
    logging.info("keep-alive: pinging %s every %s seconds", url, interval)
    return True