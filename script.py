import paramiko
import time
import os
import posixpath

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
    return output, error

def check_httpd_status(ssh_client):
    command = "systemctl status httpd"
    output = execute_ssh_command(ssh_client, command)
    if "active (running)" in output[0]:
        return True
    else:
        return False
		
checkpoint_dir = "/tmp/checkpoints/"
def create_checkpoint(ssh_client, files, service_name, checkpoint_dir):
    print("Creating checkpoint...")
    service_dir = os.path.join(checkpoint_dir, service_name)
    ssh_client.exec_command(f"mkdir -p {service_dir}")
    for file in files:
        filename = os.path.basename(file)
        command = execute_ssh_command(ssh_client, f"cat {file} > {service_dir}/{filename}")
    print(f"Checkpoint created at: {service_dir}")

def restore_files(ssh_client, files, service_name, checkpoint_dir):
    print("Restoring checkpoint...")
    service_dir = os.path.join(checkpoint_dir, service_name)
    for file in files:
        filename = os.path.basename(file)
        command = execute_ssh_command(ssh_client, f"cat {service_dir}/{filename} > {file}")
    print("Checkpoint restored and applied.")
    
def file_has_changed(ssh_client, file_path, checkpoint_file_path):
    current_content, _ = execute_ssh_command(ssh_client, f"cat {file_path}")
    checkpoint_content, _ = execute_ssh_command(ssh_client, f"cat {checkpoint_file_path}")
    return current_content != checkpoint_content

def check_and_restore_service(ssh_client, service_name, files, checkpoint_dir):
    output, _ = execute_ssh_command(ssh_client, f"systemctl is-active {service_name}")
    if output.strip() != "active":
        print(f"{service_name} is down. Checking for file modifications...")
        service_changed = False

        for file in files:
            checkpoint_file_path = posixpath.join(checkpoint_dir, service_name, posixpath.basename(file))
            
            if file_has_changed(ssh_client, file, checkpoint_file_path):
                print(f"{file} has been modified.")
                service_changed = True

        if service_changed:
            print("Changes detected, attempting to restart the service...")
            _, error = execute_ssh_command(ssh_client, f"systemctl restart {service_name}")
            if error:
                print("Restart failed, restoring from checkpoint...")
                restore_files(ssh_client, files, service_name, checkpoint_dir)
                execute_ssh_command(ssh_client, f"systemctl daemon-reload")
                execute_ssh_command(ssh_client, f"systemctl restart {service_name}")
            else:
                print(f"{service_name} restarted successfully.")
        else:
            print("No changes detected, restoring files from checkpoint...")
            restore_files(ssh_client, files, service_name, checkpoint_dir)
            execute_ssh_command(ssh_client, f"systemctl restart {service_name}")
    else:
        service_changed = False

        for file in files:
            checkpoint_file_path = posixpath.join(checkpoint_dir, service_name, posixpath.basename(file))
            if file_has_changed(ssh_client, file, checkpoint_file_path):
                print(f"{file} has been modified.")
                service_changed = True
        if service_changed:
            print("Changes detected, attempting to restart the service...")
            _, error = execute_ssh_command(ssh_client, f"systemctl restart {service_name}")
            if error:
                print("Restart failed, restoring from checkpoint...")
                restore_files(ssh_client, files, service_name, checkpoint_dir)
                execute_ssh_command(ssh_client, f"systemctl restart {service_name}")
            else:
                print(f"{service_name} restarted successfully.")
				

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

checkpoint_dir = "/tmp/checkpoints/"
first_time = True

try:
    while True:
        for vm_detail in vm_details:
            vm_ip, vm_hostname, vm_username, vm_password = vm_detail
            vm_ssh = establish_ssh_connection(vm_ip, vm_username, vm_password)
            
            for service_name, files_to_monitor in services.items():
                if first_time:
                    create_checkpoint(vm_ssh, files_to_monitor, service_name, checkpoint_dir)
                    
                check_and_restore_service(vm_ssh, service_name, files_to_monitor, checkpoint_dir)
                create_checkpoint(vm_ssh, files_to_monitor, service_name, checkpoint_dir)
                
            vm_ssh.close()
            
        first_time = False
        time.sleep(10)

except KeyboardInterrupt:
    print("Interrupted. Closing SSH connections...")
    for vm_detail in vm_details:
        vm_ip, vm_hostname, vm_username, vm_password = vm_detail
        vm_ssh = establish_ssh_connection(vm_ip, vm_username, vm_password)
        vm_ssh.close()