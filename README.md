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
  - Sysmon (with SwiftOnSecurity or Olaf Hartong config)
- **Linux VM**
  - Splunk UF or rsyslog forwarder
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

### 3: Client Machines
- **Linux VM (Ubuntu/Debian/any)**
  - we will use Debian based Linux.
  - Download The iso from Original webpage

---

## Installation & Configuration (Step-by-step)

#### 1: Linux to Virtual Box
-  Configuration are the same use the same 2 network adapter as of windows
  - 1 NAT
  - 2 Host-only Adapter












#### 2: Update Windows Sysmon Configuration
- Verify Sysmon service is running:
```bash
sc query Sysmon64
```
- Install Sysmon with **SwiftOnSecurity** config
  - Invoke-WebRequest -Uri https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/master/sysmonconfig-export.xml -OutFile C:\Temp\sysmonconfig.xml
  
```cmd
C:\Temp\Sysmon\Sysmon64.exe -c C:\Temp\sysmonconfig.xml
```
### 2: Enable extra Windows data sources
Add to `inputs.conf` (Windows UF):
```
[WinEventLog://Microsoft-Windows-PowerShell/Operational]
disabled = 0
index = win10
sourcetype = WinEventLog:PowerShell

[WinEventLog://Microsoft-Windows-Windows Defender/Operational]
disabled = 0
index = win10
sourcetype = WinEventLog:Defender

[WinEventLog://Microsoft-Windows-Sysmon/Operational]
disabled = 0
index = win10
sourcetype = WinEventLog:Microsoft-Windows-Sysmon/Operational
```

Restart:
```bash
Restart-Service SplunkForwarder
```

---

### 3: Fix Sysmon Permission Error (errorCode=5)
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
```bash
Restart-Service SplunkForwarder
```

---

### 4: Add Linux VM + Splunk UF
- Install Splunk Universal Forwarder on Linux VM
- Configure output to Kali receiver (`9997`)
- Create `inputs.conf` for key logs:

```
[monitor:///var/log/syslog]
index = linux
sourcetype = syslog
disabled = false

[monitor:///var/log/auth.log]
index = linux
sourcetype = linux_secure
disabled = false

[monitor:///var/log/kern.log]
index = linux
sourcetype = linux_kern
disabled = false

[monitor:///var/log/cron.log]
index = linux
sourcetype = linux_cron
disabled = false

[monitor:///var/log/dpkg.log]
index = linux
sourcetype = linux_pkg
disabled = false
```

Restart UF:
```bash
sudo /opt/splunkforwarder/bin/splunk restart
```

---

### 5: Validate Linux logs in Splunk
```bash
index=linux | stats count by sourcetype | sort -count
```

---

### 6: Update Win10 Dashboard
- Add panels for:
  - PowerShell Operational
  - Defender Detections
  - Sysmon DNS (Event ID 22)
  - WMI Activity (Event ID 19/20/21)

---

### 7: Create Linux Dashboard
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

## Validation Queries

**Sysmon verification**
```bash
index=win10 sourcetype="WinEventLog:Microsoft-Windows-Sysmon/Operational" | stats count by EventCode
```

**Linux SSH failures**
```bash
index=linux sourcetype=linux_secure "Failed password" | stats count by src
```

**Linux SSH success**
```bash
index=linux sourcetype=linux_secure "Accepted password" | stats count by user
```

---

## Dashboards
- **Windows SOC overview** (updated)
- **Linux SOC overview** (new)

---

## Screenshots
(Add your screenshots here)
