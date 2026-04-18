# exercise4/cmac_logic.py

# --- Use an absolute import from the project root ---
from exercise2 import aes_cipher

BLOCK_SIZE = 16
Rb = 0x87

def xor(a: bytes, b: bytes) -> bytes:
    return bytes([x ^ y for x, y in zip(a, b)])

def shift_left(b: bytes) -> bytes:
    res = int.from_bytes(b, 'big') << 1
    res &= (1 << 128) - 1 
    if (b[0] & 0x80):
        res ^= Rb
    return res.to_bytes(16, 'big')

def pad(block: bytes) -> bytes:
    return block + b'\x80' + b'\x00' * (15 - len(block))

# --- Wrapper Function to handle data type mismatch ---
def aes_encrypt_wrapper(plaintext: bytes, key: bytes) -> bytes:
    """Wrapper to convert between bytes and aes_cipher's hex string interface."""
    plaintext_hex = plaintext.hex()
    key_hex = key.hex()
    
    # Assuming your aes_encrypt returns a tuple (result_hex, log1, log2)
    result_hex, _, _ = aes_cipher.aes_encrypt(plaintext_hex, key_hex)
    
    return bytes.fromhex(result_hex)

def generate_subkeys_with_log(key: bytes) -> tuple[bytes, bytes, list]:
    """Generates K1, K2 and a structured log, with boolean flags."""
    log = []
    
    L = aes_encrypt_wrapper(b'\x00' * 16, key)
    log.append({'label': 'L = AES(key, 0)', 'value': L.hex()})

    # K1 Generation
    msb_set_for_k1 = (L[0] & 0x80)
    K1 = shift_left(L)
    log.append({'label': 'K1 Result', 'value': K1.hex(), 'xor_required': bool(msb_set_for_k1)})

    # K2 Generation
    msb_set_for_k2 = (K1[0] & 0x80)
    K2 = shift_left(K1)
    log.append({'label': 'K2 Result', 'value': K2.hex(), 'xor_required': bool(msb_set_for_k2)})
    
    return K1, K2, log

def cmac(key: bytes, msg: bytes, truncate_len: int = None) -> tuple[bytes, dict]:
    """
    Generates the CMAC tag, with optional truncation, and a structured log.
    """
    structured_log = {}
    
    K1, K2, subkey_log = generate_subkeys_with_log(key)
    structured_log['subkeys'] = subkey_log

    blocks = [msg[i:i+16] for i in range(0, len(msg), 16)]
    if not blocks:
        blocks = [b'']
    
    num_blocks = len(blocks)
    structured_log['message_info'] = {'count': num_blocks, 'blocks': [b.hex() for b in blocks]}
    
    final_block_log = []
    last_block = blocks[-1]
    
    if len(last_block) == 16:
        final_block_log.append({'type': 'info', 'text': 'Final block is a full block. Using K1.'})
        final_block_log.append({'label': 'Last Block (M_n)', 'value': last_block.hex()})
        final_block_log.append({'label': 'Subkey (K1)', 'value': K1.hex()})
        processed_last = xor(last_block, K1)
        final_block_log.append({'label': "M_n' = M_n ⊕ K1", 'value': processed_last.hex(), 'is_result': True})
    else:
        final_block_log.append({'type': 'info', 'text': f'Final block is partial ({len(last_block)} bytes). Padding and using K2.'})
        final_block_log.append({'label': 'Partial Block (M_n)', 'value': last_block.hex()})
        padded = pad(last_block)
        final_block_log.append({'label': 'Padded Block', 'value': padded.hex()})
        final_block_log.append({'label': 'Subkey (K2)', 'value': K2.hex()})
        processed_last = xor(padded, K2)
        final_block_log.append({'label': "M_n' = Padded ⊕ K2", 'value': processed_last.hex(), 'is_result': True})
        
    blocks[-1] = processed_last
    structured_log['final_block_processing'] = final_block_log

    cbc_log = []
    X = b'\x00' * 16
    
    for i, block in enumerate(blocks):
        iteration = []
        iteration.append({'label': 'Input (X_prev)', 'value': X.hex()})
        
        block_label = "M_n'" if i == num_blocks - 1 else f"M_{i+1}"
        iteration.append({'label': f'Block ({block_label})', 'value': block.hex()})
        
        X_xor_M = xor(X, block)
        iteration.append({'label': f'XOR Result (X ⊕ M)', 'value': X_xor_M.hex()})
        
        X = aes_encrypt_wrapper(X_xor_M, key)
        iteration.append({'label': f'Output (X_new)', 'value': X.hex(), 'is_result': True})
        
        cbc_log.append(iteration)
        
    structured_log['cbc_iterations'] = cbc_log

    # --- NEW: Truncation Logic ---
    full_tag = X
    final_tag = full_tag
    
    if truncate_len is not None and 1 <= truncate_len < 16:
        final_tag = full_tag[:truncate_len]
        structured_log['truncation_info'] = {
            'original_tag': full_tag.hex(),
            'final_tag': final_tag.hex(),
            'length': truncate_len
        }

    return final_tag, structured_log