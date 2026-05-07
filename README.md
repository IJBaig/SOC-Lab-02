# SOC Lab 02 (Splunk + Win10 Sysmon Enhancements + Linux Logs + Dashboards)

**Date:** 2026-06-06  
<p> Previously We created a Splunk Dashboard with Windows 10 logs and optional Sysmon now we will take it to one step further. Adding another Machine and some other steps and at the end we also simulate an attack to check if our environment will show digested data. </p>

**Note** <br>
The was an error in previous Lab in Sysmon as it was optional for that lab so we skip it but now we will resolve that issue and also add an extension to it (SwiftOnSecurity). <br>
We expand the lab with richer Sysmon telemetry, fix Sysmon permissions, add a second VM (Linux), collect rsyslog data, inhance the windows win10 dashboard and build a Linux dashboard. We also simulate SSH attacks and validate logs.

---

## Overview (What you built)
Continue from [SOC-Lab-01](https://github.com/IJBaig/SOC-Lab-01) We will:
- Enhanced Sysmon logging on Windows 10 With SwiftOnSecurity.
- Windows dashboard updated for PowerShell, Defender, DNS, and WMI
- Added a second Linux VM
- Ingest Linux logs via Splunk UF (using rsyslog)
- Fix Sysmon permission error (Event Log Readers)
- Build Linux dashboard
- Validate SSH auth activity in logs

---

## Architecture
- **Windows 10**
  - Splunk Universal Forwarder
  - Sysmon (with SwiftOnSecurity)
- **Linux VM**
  - Splunk UF and rsyslog forwarder
- **Kali Linux (Splunk Enterprise)**
  - Receiver/indexer (TCP 9997)

---

## Data Flow
Windows Event Logs / Sysmon → Splunk UF → TCP 9997 → Splunk Receiver → index (`win10`)  
Linux logs (/var/log/*) → UF / rsyslog → Splunk Receiver → index (`linux`)

---

## Prerequisites

### 1: Previous Lab
- [SOC-Lab-01](https://github.com/IJBaig/SOC-Lab-01)

### 2: Linux VM (Ubuntu/Debian/any)
  - we will use Debian based Linux.
  - Download The iso from Original webpage

---

## Installation & Configuration (Step-by-step)

#### 1: Update Windows Sysmon Configuration
- Verify Sysmon service is running:
  - ```bash
    sc query Sysmon64
    ```
- Install Sysmon with **SwiftOnSecurity** config
  - Run in Windows Powershell
    - ```powershell
      Invoke-WebRequest -Uri https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/master/sysmonconfig-export.xml -OutFile C:\Temp\sysmonconfig.xml
      ```
  - Goto to Sysmon installed Directory (in our case Downloads)
    -   ```PowerShell
        C:\Temp\Users\<yourusername>\Downloads\Sysmon\Sysmon64.exe -c C:\Temp\sysmonconfig.xml
        ```
  - Check Rule installation
    - ```cmd
      C:\Temp\Users\<yourusername>\Downloads\Sysmon\Sysmon64.exe -c
      ```
    - you will see bunch of rules or with your turtles luck no rule installed
    - just check what you did wrong or repeate the steps it will workout

#### 2: Enable extra Windows data sources
we will add 2 more DataSources Powershell and Windows Defender and also the Sysmon.
- Same as we implemented in previous Lab:
- Directory `C:\Program Files\SplunkUniversalForwarder\etc\system\local`
- Create or Replace the Content of `inputs.conf` with [win10_inputs.conf](win10_inputs.conf)

#### 3: Fix Sysmon Permission Error (errorCode=5)
Sysmon channel requires **Event Log Readers** permission.

1. Identify UF service account:
```bash
Get-WmiObject Win32_Service -Filter "Name='SplunkForwarder'" | Select Name, StartName
```

2. Add permission:
```bash
net localgroup "Event Log Readers" "NT SERVICE\SplunkForwarder" /add
```

3. Restart UF:
```PowerShell
C:\Program Files\SplunkUniversalForwarder\bin\Splunk restart
```
4. Verify:
Run the Command in Splunk web Search and Reporting app
```SPL
index=win10 | stats count by sourcetype | sort -count
```

#### 4: Linux to Virtual Box
-  Configuration are the same use the same 2 network adapter as of windows
  - 1 NAT
  - 2 Host-only Adapter

#### 5: Add Splunk UF to Linux VM
- Download [Splunk Universal Forwarder](https://www.splunk.com/en_us/download/universal-forwarder.html) .deb file on Linux VM
- Install Universal Forwarder in `/opt` folder
  - move Downloaded file to `/opt`
    - ```bash
      cd /opt
      dpkg -i <install_package_name>
      ```
- Start Splunk and set usename and password
  - ```bash
    sudo /opt/splunkforwarder/bin/splunk start --accept-license
    ```
- Configuration:
  - ```bash
    cd /opt/splunkforwarder/etc/system/local/
    vi inputs.conf
    ```
    - Copy paste the [Linux_inputs.conf](Linux_inputs.conf)
  - ```bash
    vi outputs.conf
    ```
    - Copy paste the [Linux_outputs.conf](Linux_outputs.conf)
   
  - ```bash
    sudo systemctl enable --now rsyslog
    sudo systemctl restart rsyslog
    sudo /opt/splunkforwarder/bin/splunk enable boot-start
    sudo /opt/splunkforwarder/bin/splunk restart
    ```
- Validate Linux logs in Splunk
  - ```bash
    index=linux | stats count by sourcetype | sort -count
    ```
---

### 6: DashBoards
#### Update Win10 Dashboard
Complete Upaded Classic Dashboard xml code is at [win10_Dashboard.xml](win10_Dasboard.xml)
- Along with previous panels new were added:
  - PowerShell Operational
  - Defender Detections
  - Sysmon DNS (Event ID 22)
  - WMI Activity (Event ID 19/20/21)


#### 7: Create Linux Dashboard
Complete Classic Dashboard xml code is at [Linux_Dashboard.xml](Linux_Dasboard.xml)
Create a full Linux baseline dashboard with panels:
- Event volume by host
- Events over time
- Top sourcetypes
- SSH success/fail summary
- SSH src IPs (failed/success)
- Unique SSH users
- Sudo usage + commands
- New user creation
- User added to sudo/wheel
- Cron activity and commands
- Kernel warnings/errors
- Package installs/updates
- Rare messages
- Auth failures (non-SSH)

---

## SSH Attack (Simulation)
### SSH brute force / failed login test

---
