# exercise4/md5_logic.py
import math

# --- 1. Core MD5 Functions (Unchanged) ---
def F(b, c, d): return (b & c) | ((~b & 0xFFFFFFFF) & d)
def G(b, c, d): return (b & d) | (c & (~d & 0xFFFFFFFF))
def H(b, c, d): return b ^ c ^ d
def I(b, c, d): return c ^ (b | (~d & 0xFFFFFFFF))

def left_rotate(x, amount):
    x &= 0xFFFFFFFF
    return ((x << amount) | (x >> (32 - amount))) & 0xFFFFFFFF

# --- 2. Block Splitting with Logging ---
def split_into_blocks_with_log(st: bytes) -> tuple[list, dict]:
    """Splits a message into blocks and returns a detailed log of the padding process."""
    log = {}
    data = bytearray(st)
    
    log['original_message_hex'] = data.hex()
    log['original_len_bytes'] = len(data)
    orig_len_bits = len(data) * 8
    log['original_len_bits'] = orig_len_bits

    data.append(0x80)
    log['appended_80'] = True

    padding_needed = (56 - len(data) % 64 + 64) % 64
    data.extend(b'\x00' * padding_needed)
    log['zero_padding_bytes'] = padding_needed

    data.extend(orig_len_bits.to_bytes(8, byteorder='little'))
    log['length_appended_hex'] = (orig_len_bits.to_bytes(8, byteorder='little')).hex()
    
    log['final_padded_message_hex'] = data.hex()

    blocks = [data[i:i + 64] for i in range(0, len(data), 64)]
    return blocks, log

# --- 3. Main MD5 Implementation with Logging ---
def md5_hash(message: bytes) -> tuple[str, dict]:
    """Calculates the MD5 hash and returns the hex digest and a structured log."""
    structured_log = {}

    # --- Initial State ---
    a0 = 0x67452301
    b0 = 0xefcdab89
    c0 = 0x98badcfe
    d0 = 0x10325476
    structured_log['initial_state'] = {
        'a0': f'{a0:08x}', 'b0': f'{b0:08x}',
        'c0': f'{c0:08x}', 'd0': f'{d0:08x}'
    }

    # --- Padding and Block Splitting ---
    chunks, padding_log = split_into_blocks_with_log(message)
    structured_log['padding_info'] = padding_log

    # --- Pre-computation (K and S constants) ---
    K = [int((1 << 32) * abs(math.sin(i + 1))) & 0xFFFFFFFF for i in range(64)]
    shifts = [
        7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
        5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
        4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
        6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21
    ]

    # --- Block Processing ---
    structured_log['blocks'] = []
    
    # These are the cumulative hash values
    h0, h1, h2, h3 = a0, b0, c0, d0

    for i, block in enumerate(chunks):
        current_block_log = {'block_index': i + 1, 'rounds': []}
        
        M = [int.from_bytes(block[k*4:(k+1)*4], byteorder='little') for k in range(16)]
        
        A, B, C, D = h0, h1, h2, h3
        current_block_log['initial_abcd'] = {
            'A': f'{A:08x}', 'B': f'{B:08x}',
            'C': f'{C:08x}', 'D': f'{D:08x}'
        }

        # Main loop: 64 operations
        for j in range(64):
            round_log = {'j': j}
            if 0 <= j <= 15:
                f_val = F(B, C, D)
                g_idx = j
                round_log['func'] = f"F(B,C,D) = {f_val:08x}"
            elif 16 <= j <= 31:
                f_val = G(B, C, D)
                g_idx = (5 * j + 1) % 16
                round_log['func'] = f"G(B,C,D) = {f_val:08x}"
            elif 32 <= j <= 47:
                f_val = H(B, C, D)
                g_idx = (3 * j + 5) % 16
                round_log['func'] = f"H(B,C,D) = {f_val:08x}"
            elif 48 <= j <= 63:
                f_val = I(B, C, D)
                g_idx = (7 * j) % 16
                round_log['func'] = f"I(B,C,D) = {f_val:08x}"

            # Core MD5 mixing formula
            temp = (f_val + A + K[j] + M[g_idx]) & 0xFFFFFFFF
            
            # Store values before update for the log
            round_log['A_prev'] = f'{A:08x}'
            
            # Update registers
            A = D
            D = C
            C = B
            B = (B + left_rotate(temp, shifts[j])) & 0xFFFFFFFF
            
            # Store new values in the log
            round_log['A_new'] = f'{A:08x}'
            round_log['B_new'] = f'{B:08x}'
            round_log['C_new'] = f'{C:08x}'
            round_log['D_new'] = f'{D:08x}'
            
            current_block_log['rounds'].append(round_log)

        # Add this block's hash to the cumulative sum
        h0 = (h0 + A) & 0xFFFFFFFF
        h1 = (h1 + B) & 0xFFFFFFFF
        h2 = (h2 + C) & 0xFFFFFFFF
        h3 = (h3 + D) & 0xFFFFFFFF
        
        current_block_log['final_abcd'] = {
            'h0': f'{h0:08x}', 'h1': f'{h1:08x}',
            'h2': f'{h2:08x}', 'h3': f'{h3:08x}'
        }
        structured_log['blocks'].append(current_block_log)

    # --- Final Output ---
    final_hash = bytearray()
    final_hash.extend(h0.to_bytes(4, byteorder='little'))
    final_hash.extend(h1.to_bytes(4, byteorder='little'))
    final_hash.extend(h2.to_bytes(4, byteorder='little'))
    final_hash.extend(h3.to_bytes(4, byteorder='little'))
    
    structured_log['final_hash'] = final_hash.hex()
    return final_hash.hex(), structured_log