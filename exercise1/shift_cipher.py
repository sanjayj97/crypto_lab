# shift_cipher.py
from .crypto_utils import char_to_index, index_to_lower_char, index_to_upper_char

def validate_key(key):
    try:
        k = int(key)
    except ValueError:
        raise ValueError("Key must be an integer.")
    
    # THE CHECK YOU REQUESTED
    if k < 0 or k > 25:
        raise ValueError("Key must be between 0 and 25.")
        
    return k

def encrypt_shift(plaintext, key):
    try: k = int(key)
    except ValueError: raise ValueError("Key must be an integer.")
    res = []
    for ch in plaintext:
        idx = char_to_index(ch)
        if idx == -1: res.append(ch)
        else: res.append(index_to_upper_char(idx + k))
    return "".join(res)

def decrypt_shift(ciphertext, key):
    try: k = int(key)
    except ValueError: raise ValueError("Key must be an integer.")
    res = []
    for ch in ciphertext:
        idx = char_to_index(ch)
        if idx == -1: res.append(ch)
        else: res.append(index_to_lower_char(idx - k))
    return "".join(res)