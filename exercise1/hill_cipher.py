# hill_cipher.py
import math
from .crypto_utils import (
    char_to_index, 
    index_to_lower_char, 
    index_to_upper_char,
    mod_inverse,   # Imported math
    gcd            # Imported math (optional if math.gcd is used, but consistency is good)
)

MOD = 26

def mod(n, m=MOD): 
    return ((n % m) + m) % m

def parse_square_matrix(text, size):
    try: size = int(size)
    except: raise ValueError("Size must be an integer.")
    if size <= 0: raise ValueError("Dimension must be positive.")
    
    tokens = text.replace(',', ' ').split()
    if len(tokens) != size * size:
        raise ValueError(f"Expected {size*size} values, got {len(tokens)}.")
    
    matrix = []
    it = iter(tokens)
    try:
        for _ in range(size):
            matrix.append([int(next(it)) for _ in range(size)])
    except ValueError: raise ValueError("Matrix entries must be integers.")
    return matrix

def determinant(m):
    if len(m) == 1: return m[0][0]
    if len(m) == 2: return m[0][0]*m[1][1] - m[0][1]*m[1][0]
    det = 0
    for c in range(len(m)):
        det += ((-1)**c) * m[0][c] * determinant([row[:c] + row[c+1:] for row in m[1:]])
    return det

def transpose(m):
    return [[m[j][i] for j in range(len(m))] for i in range(len(m[0]))]

def cofactor_matrix(m):
    n = len(m)
    cof = [[0]*n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            minor = [row[:c] + row[c+1:] for row in (m[:r] + m[r+1:])]
            cof[r][c] = ((-1)**(r+c)) * determinant(minor)
    return cof

def inverse_matrix_mod26(m):
    det = determinant(m)
    # Using mod_inverse from crypto_utils
    det_inv = mod_inverse(det, 26) 
    cof = cofactor_matrix(m)
    adj = transpose(cof)
    return [[mod(val * det_inv, 26) for val in row] for row in adj]

def encrypt_hill(plaintext, matrix):
    n = len(matrix)
    # Using crypto_utils.gcd or math.gcd
    if gcd(mod(determinant(matrix)), 26) != 1:
        raise ValueError("Key matrix not invertible mod 26.")
    
    indices = [char_to_index(c) for c in plaintext if char_to_index(c) != -1]
    if not indices: raise ValueError("No valid letters in plaintext.")
    while len(indices) % n != 0: indices.append(char_to_index('x'))
    
    res = ""
    for i in range(0, len(indices), n):
        vec = indices[i:i+n]
        for j in range(n):
            val = sum(vec[k] * matrix[k][j] for k in range(n))
            res += index_to_upper_char(val)
    return res

def decrypt_hill(ciphertext, matrix):
    inv_matrix = inverse_matrix_mod26(matrix)
    n = len(matrix)
    indices = [char_to_index(c) for c in ciphertext if char_to_index(c) != -1]
    
    if len(indices) % n != 0: raise ValueError("Ciphertext length invalid.")
    
    res = ""
    for i in range(0, len(indices), n):
        vec = indices[i:i+n]
        for j in range(n):
            val = sum(vec[k] * inv_matrix[k][j] for k in range(n))
            res += index_to_lower_char(int(round(val)))
    return res