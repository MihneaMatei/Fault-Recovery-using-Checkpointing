# Fault Recovery System Using Checkpointing
## Description
This repository contains the implementation of a fault recovery system using checkpointing designed for a distributed environment with two virtual machines (VM1 and VM2). VM1 acts as the primary node running essential services and a checkpointing script, while VM2 serves as a secondary node that monitors VM1 and takes over in case of a failure. This setup ensures minimal downtime and maximizes data integrity. The services monitored are httpd and nginx, but they can be modified in the services.txt file. The VMs can be adjusted in vms.txt.

## Features
**Automated Checkpointing:** Regular snapshots to capture the system state.

**Automated Recovery:** In case of failure, automated recovery process for monitored services.

**Failure Monitoring:** Continuous monitoring of VM1 by VM2.

**Automated Failover:** Seamless transition of duties from VM1 to VM2 during failures.

**HTTP Server for Monitoring:** VM1 hosts an HTTP server that provides a live status of the system.

**Automated Fault Injeection Script:** A script to inject faults in the services (it either stops the service or corrupts configuration files).

## Installation
**Prerequisites**

Python 3.6 or higher
Flask
Paramiko
OpenSSH
Access to two VMs or physical machines with nginx and httpd (for the current setup)

**Setup Instructions** 

1. Clone the Repository

```console
git clone https://github.com/MihneaMatei/Fault-Recovery-using-Checkpointing.git
cd Fault-Recovery-using-Checkpointing
```

**IMPORTANT NOTE: The easiest and fastest way to run seamlessly is to clone the repository on both VMs (or all VMs if the setup was changed).**

**Install Dependencies**

```console
pip install paramiko Flask python3 openssh-server
```

**IMPORTANT NOTE: The easiest and fastest way to run seamlessly is to install the dependencies on all VMs.**

**Configure the machines**

Ensure both VMs are networked correctly and can access each other. Set up SSH access between the machines.

**Usage**

To start the system:

On VM1:

```console
cd Fault-Recovery-using-Checkpointing
python server.py &       # Starts the HTTP server in the background
python script.py &       # Starts the fault-recovery script in the background
```

On VM2:

```console
cd Fault-Recovery-using-Checkpointing
python monitor.py &      # Starts the monitoring and failover script in the background
```

To inject faults automatically, run on any VM:

```console
python fault_injection.py &
```

**For more details, check the documentation file (.PDF) in the repository.**

## Author
Mihnea-Cristian Matei, Student@ACS-UPB
