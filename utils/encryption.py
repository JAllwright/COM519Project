import hashlib
import os
import binascii

def hash_password(password):
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        100000
    )
    return f"{binascii.hexlify(salt).decode()}:{binascii.hexlify(hashed_password).decode()}"

def verify_password(stored_password, entered_password):

    salt, hashed_password = stored_password.split(':')  # Extract salt and hash
    salt = binascii.unhexlify(salt)
    hashed_entered_password = hashlib.pbkdf2_hmac(
        'sha256',
        entered_password.encode(),
        salt,
        100000
    )
    return binascii.hexlify(hashed_entered_password).decode() == hashed_password
