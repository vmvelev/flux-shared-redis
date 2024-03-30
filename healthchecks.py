from redis import Redis
import requests
import time
from functions import *
from datetime import datetime

app_name = "chocohostingstg"
redis_port = 33777
redis_username = "username"
redis_password = "password"

print("Starting health checks")

res = requests.get(f"https://api.runonflux.io/apps/location/{app_name}")
ips = []
if res.status_code == 200 and res.json().get("status") == "success":
    for location in res.json().get("data"):
        ip = location.get("ip")
        if ":" in ip:
            ip = ip.split(":")[0]
        ips.append(ip)

for ip in ips:
    try:
        redis = Redis(host=ip, port=redis_port, username=redis_username, password=redis_password, socket_timeout=3)
        response = redis.role()
        print(response[0].decode())
    except Exception as e:
        print(e)
        print(f"Failed to connect to - {ip}")
        continue

# master_ip = ips[0]
# replica_1_ip = ips[1]
# replica_2_ip = ips[2]

# redis_master = Redis(host=master_ip, port=redis_port, username=redis_username, password=redis_password)

# while True:
#     # Checking if master is alive
#     try:
#         redis = Redis(host=master_ip, port=redis_port, username=redis_username, password=redis_password, socket_timeout=3)
#         # master_ip, replica_1_ip, replica_2_ip = get_master_and_replicas(redis)
#         response = redis.ping()
#     except Exception as e:
#         print(e)
#         current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         print(f"{current_time} - Promoting replica 1 to master")
#         redis_replica_1 = Redis(host=replica_1_ip, port=redis_port, username=redis_username, password=redis_password, socket_timeout=3)
#         redis_replica_1.config_set("masteruser", "")
#         redis_replica_1.config_set("masterauth", "")
#         redis_replica_1.execute_command("REPLICAOF NO ONE")
#         response = redis_replica_1.set("master", replica_1_ip)
#         response = redis_replica_1.set("replica_1", replica_2_ip)
#         response = redis_replica_1.set("replica_2", "")
#         master_ip = replica_1_ip
#         replica_1_ip = replica_2_ip
#         replica_2_ip = None
#         redis_replica_1 = Redis(host=replica_1_ip, port=redis_port, username=redis_username, password=redis_password, socket_timeout=3)
#         redis_replica_1.config_set("masteruser", redis_username)
#         redis_replica_1.config_set("masterauth", redis_password)
#         redis_replica_1.execute_command(f"REPLICAOF {master_ip} {redis_port}")
#         continue
#     # Get current timestamp
#     current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     print(f"{current_time} - All nodes are healthy")
#     print(f"{current_time} - Master IP - {master_ip}")
#     print(f"{current_time} - Replica 1 IP - {replica_1_ip}")
#     print(f"{current_time} - Replica 2 IP - {replica_2_ip}")
#     time.sleep(10)