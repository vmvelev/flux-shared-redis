import requests
from redis import Redis
from functions import *

app_name = "chocohostingstg"
redis_port = 33777
redis_username = "username"
redis_password = "password"

try:
    res = requests.get(f"https://api.runonflux.io/apps/location/{app_name}")
    ips = []

    if res.status_code == 200 and res.json().get("status") == "success":
        for location in res.json().get("data"):
            ip = location.get("ip")
            if ":" in ip:
                ip = ip.split(":")[0]
            ips.append(ip)
except Exception as e:
    print(e)
    print(f"{get_current_time()} - Failed to get IPs from API")
    exit()

print(f"{get_current_time()} - All nodes: {ips}")

print(f"{get_current_time()} - Checking if master is already setup")
count_master = 0
count_replica = 0
for ip in ips:
    try:
        redis = Redis(host=ip, port=redis_port, username=redis_username, password=redis_password, socket_timeout=3)
        response = redis.role()[0].decode()
        if response == "master":
            count_master += 1
        elif response == "slave":
            count_replica += 1
    except Exception as e:
        print(e)
        print(f"{get_current_time()} - Failed to connect to - {ip}")
        continue

if count_master == 1 and count_replica == len(ips) - 1:
    print(f"{get_current_time()} - Master and replicas are already setup")
    print(f"{get_current_time()} - Starting health checks")
    # TODO: Start health checks
    exit()

if count_master > 1:
    print(f"{get_current_time()} - Multiple masters found. Checking if there is data in redis.")
    master_ips = []
    for ip in ips:
        try:
            redis = Redis(host=ip, port=redis_port, username=redis_username, password=redis_password, socket_timeout=3)
            response = redis.get("master")
            if response is not None:
                if response.decode() not in master_ips:
                    master_ips.append(response.decode())
        except Exception as e:
            print(e)
            print(f"{get_current_time()} - Failed to connect to - {ip}")
            continue
    if len(master_ips) == 1:
        print(f"{get_current_time()} - Found single master in redis. Setting up replicas.")
        master_ip = master_ips[0]
        for ip in ips:
            try:
                redis = Redis(host=ip, port=redis_port, username=redis_username, password=redis_password, socket_timeout=3)
                if ip != master_ip:
                    print(f"{get_current_time()} - Setting up replica - {ip}")
                    redis.config_set("masteruser", redis_username)
                    redis.config_set("masterauth", redis_password)
                    redis.execute_command(f"REPLICAOF {master_ip} {redis_port}")
                    response = redis.role()[0].decode()
                    if response == "slave":
                        print(f"{get_current_time()} - Successfully setup replica - {ip}")
            except Exception as e:
                print(e)
                print(f"{get_current_time()} - Failed to setup replica - {ip}")
    if len(master_ips) == 0:
        print(f"{get_current_time()} - No master IP in redis. Starting initial setup.")

master_ip = ips[0]

print(f"{get_current_time()} - Setting up master - {master_ip}")
redis_master = Redis(host=master_ip, port=redis_port, username=redis_username, password=redis_password, socket_timeout=3)
redis_master.execute_command("REPLICAOF NO ONE")
response = redis_master.role()[0].decode()
if response == "master":
    print(f"{get_current_time()} - Successfully setup master - {master_ip}")

for ip in ips[1:]:
    try:
        redis = Redis(host=ip, port=redis_port, username=redis_username, password=redis_password, socket_timeout=3)
        if ip != master_ip:
            print(f"{get_current_time()} - Setting up replica - {ip}")
            redis.config_set("masteruser", redis_username)
            redis.config_set("masterauth", redis_password)
            redis.execute_command(f"REPLICAOF {master_ip} {redis_port}")
            response = redis.role()[0].decode()
            if response == "slave":
                print(f"{get_current_time()} - Successfully setup replica - {ip}")
    except Exception as e:
        print(e)
        print(f"{get_current_time()} - Failed to setup replica - {ip}")

print(f"{get_current_time()} - Writing master IP in redis")
redis = Redis(host=master_ip, port=redis_port, username=redis_username, password=redis_password, socket_timeout=3)
redis.set("master", master_ip)
response = redis.get("master").decode()
if response == master_ip:
    print(f"{get_current_time()} - Successfully written master IP in redis")

print(f"{get_current_time()} - Writing replica IPs in redis")
replica_ips = ips[1:]
for i, replica_ip in enumerate(replica_ips):
    redis = Redis(host=master_ip, port=redis_port, username=redis_username, password=redis_password, socket_timeout=3)
    redis.set(f"replica_{i+1}", replica_ip)
    response = redis.get(f"replica_{i+1}").decode()
    if response == replica_ip:
        print(f"{get_current_time()} - Successfully written replica {i+1} IP in redis")

print(f"{get_current_time()} - Initial setup completed")
print(f"{get_current_time()} - Starting health checks")