# crypto_utils.py

# ============================
# 1. CHARACTER UTILITIES
# ============================

def char_to_index(ch):
    if not isinstance(ch, str) or len(ch) != 1: 
        return -1
    code = ord(ch.lower())
    if 97 <= code <= 122:
        return code - 97
    return -1

def index_to_lower_char(index):
    return chr(97 + (index % 26))

def index_to_upper_char(index):
    return chr(65 + (index % 26))


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def extended_gcd(a, b):
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
        
    return old_r, old_s, old_t

def extended_gcd_verbose(a, b):
    steps = []
    
    # r = remainder, s = coeff for a, t = coeff for b
    # r0 = q*r1 + r2
    
    r0, r1 = a, b
    s0, s1 = 1, 0
    t0, t1 = 0, 1
    
    # Record initial state
    # We want a table row: q | r | s | t
    # For the setup rows where there is no q yet:
    steps.append({'q': '-', 'r': r0, 's': s0, 't': t0})
    steps.append({'q': '-', 'r': r1, 's': s1, 't': t1})
    
    while r1 != 0:
        q = r0 // r1
        r2 = r0 % r1
        
        s2 = s0 - q * s1
        t2 = t0 - q * t1
        
        # Record this step
        steps.append({'q': q, 'r': r2, 's': s2, 't': t2})
        
        # Shift for next iteration
        r0, r1 = r1, r2
        s0, s1 = s1, s2
        t0, t1 = t1, t2
        
    return r0, s0, t0, steps

def mod_inverse(a, m):
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError(f"No inverse for {a} mod {m} (gcd={g}).")
    return (x % m + m) % m