

def evaluate_health(result):
    if not result["reachable"]:
        return "Down"

    status_code = result["status_code"]
    response_time = result["response_time_ms"]

    if status_code >= 500:
        return "Down"

    if status_code >= 400:
        return "Degraded"

    if status_code > 2000:
        return "Degraded"

    if 200 <= status_code < 400:
        return "Healthy"

    return "Degraded"
