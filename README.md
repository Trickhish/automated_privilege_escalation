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
