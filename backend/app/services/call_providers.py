"""Which service the learner/mentor calls run on.

The call buttons show a "Call with" picker listing the services in CALL_PROVIDERS (comma-separated).
It defaults to "jitsi,livekit": both are shown. A service that is not set up yet is shown greyed out as
"not set up", and the first one that works is selected. List only one service to hide the picker.
Services:
    jitsi    a link to a Jitsi room. No setup, but the public server asks the first person in to sign in.
    livekit  an in-app call page (/call/<submission id>) on LiveKit. Needs LIVEKIT_URL, LIVEKIT_API_KEY and
             LIVEKIT_API_SECRET, and `pip install livekit-api`.
LiveKit counts as set up once LIVEKIT_URL, LIVEKIT_API_KEY and LIVEKIT_API_SECRET are set and the
livekit-api package is installed.
(The older single CALL_PROVIDER setting still works if CALL_PROVIDERS is not set.)

Folio's own WebRTC would be added here later as a third provider: a new branch in call_links, plus its own
signaling route. The pages already read `call.provider`, so they only need a new call screen.
"""
import importlib.util
import logging
import os
from datetime import timedelta

PROVIDERS = ("jitsi", "livekit")
LABELS = {"jitsi": "Jitsi", "livekit": "LiveKit"}
LIVEKIT_TOKEN_MINUTES = 60   # how long a token can be used to join; calls already running are not cut off


class CallNotConfiguredError(Exception):
    """The chosen call provider is missing settings."""


def enabled_providers():
    """The services listed in the picker, in order."""
    raw = os.environ.get("CALL_PROVIDERS") or os.environ.get("CALL_PROVIDER") or "jitsi,livekit"
    names = []
    for name in (n.strip().lower() for n in raw.split(",")):
        if name in PROVIDERS:
            if name not in names:
                names.append(name)
        elif name:
            logging.warning("Unknown call provider %r ignored", name)
    return names or ["jitsi", "livekit"]   # same as the default


def livekit_configured():
    if not (os.environ.get("LIVEKIT_URL") and os.environ.get("LIVEKIT_API_KEY") and os.environ.get("LIVEKIT_API_SECRET")):
        return False
    try:
        return importlib.util.find_spec("livekit.api") is not None
    except ImportError:
        return False


def is_available(provider):
    """Jitsi needs no setup. LiveKit needs its keys and the livekit-api package."""
    return livekit_configured() if provider == "livekit" else True


def room_name(submission):
    """From the submission's random id, so the room can't be guessed. Only the learner and
    the exercise's mentor are ever given it."""
    return f"folio-{submission.id}"


def _links_for(provider, submission):
    if provider == "livekit":
        return {
            "provider": "livekit", "label": LABELS["livekit"],
            "video": f"/call/{submission.id}?mode=video",
            "voice": f"/call/{submission.id}?mode=voice",
        }

    room = room_name(submission)
    # Set CALL_URL_TEMPLATE and VOICE_CALL_URL_TEMPLATE (with {room}) to point at another link-based service.
    video = os.environ.get("CALL_URL_TEMPLATE") or "https://meet.jit.si/{room}"   # empty counts as not set
    voice = os.environ.get("VOICE_CALL_URL_TEMPLATE") or "https://meet.jit.si/{room}#config.startWithVideoMuted=true"
    return {
        "provider": "jitsi", "label": LABELS["jitsi"],
        "video": video.replace("{room}", room), "voice": voice.replace("{room}", room),
    }


def call_links(submission):
    """What the call buttons show. `options` lists every service in the picker, each marked
    available or not. The top-level provider/video/voice repeat the default (the first
    available one), so older pages keep working."""
    options = []
    for provider in enabled_providers():
        option = _links_for(provider, submission)
        option["available"] = is_available(provider)
        options.append(option)
    default = next((o for o in options if o["available"]), options[0])
    return {**default, "options": options}


def livekit_token(submission, user_id, display_name, mode):
    """A short-lived pass for one person to join this submission's room."""
    url = os.environ.get("LIVEKIT_URL")
    key = os.environ.get("LIVEKIT_API_KEY")
    secret = os.environ.get("LIVEKIT_API_SECRET")
    if not (url and key and secret):
        raise CallNotConfiguredError()

    try:
        from livekit.api import AccessToken, VideoGrants   # only needed when LiveKit is used
    except ImportError as err:
        raise CallNotConfiguredError() from err

    token = (
        AccessToken(key, secret)
        .with_identity(str(user_id))
        .with_name(display_name or "Folio user")
        .with_ttl(timedelta(minutes=LIVEKIT_TOKEN_MINUTES))
        .with_grants(VideoGrants(room_join=True, room=room_name(submission), can_publish=True, can_subscribe=True))
        .to_jwt()
    )
    return {"token": token, "url": url, "room": room_name(submission), "mode": mode}