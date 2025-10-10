import bcrypt

pw = b"isi_disini"
hashed = bcrypt.hashpw(pw, bcrypt.gensalt())
print("Hash untuk secrets.toml:")
print(hashed.decode())
