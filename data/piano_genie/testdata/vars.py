import json

variables_fp = 'stp_iq_auto_dt.json'

with open(variables_fp, 'r') as f:
    variables = json.loads(f.read())