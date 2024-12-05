from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Cipher import AES
import base64
import os
from dotenv import load_dotenv
import hashlib

class AesService:
    load_dotenv(".env")
    key = base64.b64decode(os.getenv("AES_KEY").encode())
    iv = base64.b64decode(os.getenv("AES_IV").encode())

    def encrypt(data: str) -> str:
        cipher = AES.new(AesService.key, AES.MODE_CBC, AesService.iv)
        padded_data = pad(data.encode(), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(AesService.iv + encrypted).decode()

    def sha1(data: str) -> str:
        return hashlib.sha1(data.encode()).hexdigest()

    def decrypt(encrypted_data: str) -> str:
        decoded_data = base64.b64decode(encrypted_data)
        iv_received = decoded_data[:16]
        encrypted = decoded_data[16:]
        cipher = AES.new(AesService.key, AES.MODE_CBC, iv_received)
        return unpad(cipher.decrypt(encrypted), AES.block_size).decode()