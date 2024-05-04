from cryptography.fernet import Fernet

# 生成密钥
key = Fernet.generate_key()

# 将密钥保存到文件
with open('key.txt', 'wb') as key_file:
    key_file.write(key)