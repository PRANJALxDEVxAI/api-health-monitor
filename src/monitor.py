
import time
import requests


def check_api(url):
    start_time = time.perf_counter()

    try:
        response = requests.get(url, timeout=10)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return {
            "url": url,
            "status_code": response.status_code,
            "response_time_ms": round(elapsed_ms, 2),
            "reachable": True,
            "error": None
        }

    except requests.exceptions.Timeout:
        return {
            "url": url,
            "status_code": None,
            "response_time_ms": None,
            "reachable": False,
            "error": "Request timed out"
        }

    except requests.exceptions.RequestException as error:
        return {
            "url": url,
            "status_code": None,
            "response_time_ms": None,
            "reachable": False,
            "error": str(error)
        }
