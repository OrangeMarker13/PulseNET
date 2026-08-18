import hashlib
import json
import os
import time


CACHE_DIRECTORY = ".pulsegrid_cache"
DEFAULT_CACHE_SECONDS = 900


def create_cache_directory():
    os.makedirs(
        CACHE_DIRECTORY,
        exist_ok=True
    )


def create_cache_key(
    name,
    parameters
):
    content = json.dumps(
        parameters,
        sort_keys=True,
        default=str
    )

    return hashlib.sha256(
        f"{name}:{content}".encode("utf-8")
    ).hexdigest()


def get_cache_path(key):
    create_cache_directory()

    return os.path.join(
        CACHE_DIRECTORY,
        f"{key}.json"
    )


def save_cache(
    key,
    data
):
    path = get_cache_path(key)

    cache_data = {
        "timestamp": time.time(),
        "data": data
    }

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            cache_data,
            file
        )


def load_cache(
    key,
    max_age=DEFAULT_CACHE_SECONDS
):
    path = get_cache_path(key)

    if not os.path.exists(path):
        return None

    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:
            cache_data = json.load(file)

        timestamp = cache_data.get(
            "timestamp"
        )

        if timestamp is None:
            return None

        age = time.time() - timestamp

        if age > max_age:
            return None

        return cache_data.get("data")

    except (
        OSError,
        json.JSONDecodeError
    ):
        return None


def clear_cache():
    if not os.path.exists(
        CACHE_DIRECTORY
    ):
        return

    for filename in os.listdir(
        CACHE_DIRECTORY
    ):
        path = os.path.join(
            CACHE_DIRECTORY,
            filename
        )

        if os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass
