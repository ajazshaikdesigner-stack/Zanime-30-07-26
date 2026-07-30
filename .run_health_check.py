from src.core.managers.health_check_manager import HealthCheckManager
import json

h = HealthCheckManager()
r = h.run_all_checks()
print(json.dumps(r, indent=2))
