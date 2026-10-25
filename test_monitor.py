
from src.monitor import check_api
from src.health_check import evaluate_health

url = "https://httpbin.org/get"

result = check_api(url)
health = evaluate_health(result)

print("Monitoring result:", result)
print("Health status:", health)
