import paramiko
import random
import time

def establish_ssh_connection(hostname, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)
    return client

def execute_ssh_command(ssh_client, command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    if error:
        print(f"Error executing command '{command}': {error}")
    return output

def inject_fault(ssh_client, service_name, files):
    fault_type = random.choice(['stop_service', 'corrupt_file'])
    
    if fault_type == 'stop_service':
        print(f"Stopping {service_name}...")
        execute_ssh_command(ssh_client, f"systemctl stop {service_name}")
        print(f"{service_name} stopped for fault injection.")
    elif fault_type == 'corrupt_file':
        # Randomly select a file to corrupt
        file_to_corrupt = random.choice(files)
        print(f"Corrupting file {file_to_corrupt}...")
        execute_ssh_command(ssh_client, f"echo 'Corrupted content!' > {file_to_corrupt}")
        print(f"Injected corruption into {file_to_corrupt}.")
		
vm_details_file = "vms.txt"

vm_details = []
with open(vm_details_file, "r") as file:
    for line in file:
        vm_details.append(line.strip().split())

service_file = "services.txt"
services = {}
with open(service_file, "r") as file:
    for line in file:
        parts = line.strip().split()
        service_name = parts[0]
        files_to_monitor = parts[1:]
        services[service_name] = files_to_monitor
        
try:
    while True:
        for vm_detail in vm_details:
            vm_ip, vm_hostname, vm_username, vm_password = vm_detail
            vm_ssh = establish_ssh_connection(vm_ip, vm_username, vm_password)
            
            service_name, files = random.choice(list(services.items()))
            inject_fault(vm_ssh, service_name, files)
            vm_ssh.close()
        print("Fault injection complete. Waiting for next round...")
        time.sleep(60)  # Wait for 60 seconds before next fault injection round

except KeyboardInterrupt:
    print("Fault injection script terminated.")