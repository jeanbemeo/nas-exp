import requests

synology_host = "http://10.9.118.221:5000"  # Ganti dengan IP/NAS yang sesuai
username = "nasAdmin"  # Ganti dengan username Anda
password = "nasAdmin"  # Ganti dengan password Anda
session_name = "FileStation"

login_url = f"{synology_host}/webapi/auth.cgi"

params = {
    "api": "SYNO.API.Auth",
    "version": "6",
    "method": "login",
    "account": username,
    "passwd": password,
    "session": session_name,
    "format": "cookie"
}

response = requests.get(login_url, params=params)

if response.status_code == 200:
    data = response.json()
    if data.get("success"):
        print(f"Login berhasil! Session ID: {data['data']['sid']}")
        sid = data["data"]["sid"]
    else:
        print("Login gagal:", data)
else:
    print("Request error:", response.status_code)
