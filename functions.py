from datetime import datetime

def get_master_and_replicas(redis):
    response = redis.get("master")
    master_ip = response.decode("utf-8")
    response = redis.get("replica_1")
    replica_1_ip = response.decode("utf-8")
    response = redis.get("replica_2")
    replica_2_ip = response.decode("utf-8")
    return master_ip, replica_1_ip, replica_2_ip

def exeucte_replica_of(redis, ip, port, username, password):
    if port is None:
        redis.execute_command("REPLICAOF NO ONE")
    else:
        redis.config_set("masteruser", username)
        redis.config_set("masterauth", password)
        redis.execute_command(f"REPLICAOF {ip} {port}")

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")