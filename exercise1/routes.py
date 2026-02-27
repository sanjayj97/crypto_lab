# exercise1/routes.py
from flask import render_template, request, redirect, url_for
from . import ex1_bp  # Import the blueprint we created in __init__.py

# Import your modules using relative imports (from . import ...)
from . import shift_cipher
from . import hill_cipher
from . import playfair_cipher
from . import primitive_root
from . import crypto_utils

# --- Routes ---

# Note: We don't need the '/' root route here, that stays in the main app.py

@ex1_bp.route('/shift', methods=['GET', 'POST'])
def shift_route():
    result, error, mode = None, None, None
    if request.method == 'POST':
        try:
            pt = request.form.get('text', '')
            key = request.form.get('key', '')
            
            if 'encrypt' in request.form:
                result = shift_cipher.encrypt_shift(pt, key)
                mode = "Ciphertext"
            elif 'decrypt' in request.form:
                result = shift_cipher.decrypt_shift(pt, key)
                mode = "Plaintext"
        except Exception as e: error = str(e)
    return render_template('shift.html', result=result, error=error, mode=mode)

@ex1_bp.route('/playfair', methods=['GET', 'POST'])
def playfair_route():
    data, error, mode = None, None, None
    if request.method == 'POST':
        try:
            text = request.form.get('text', '')
            key = request.form.get('key', '')
            
            if 'encrypt' in request.form:
                data = playfair_cipher.playfair_process(text, key, 'encrypt')
                mode = "Encryption"
            elif 'decrypt' in request.form:
                data = playfair_cipher.playfair_process(text, key, 'decrypt')
                mode = "Decryption"
        except Exception as e: error = str(e)
    return render_template('playfair.html', data=data, error=error, mode=mode)

@ex1_bp.route('/hill_crypto', methods=['GET', 'POST'])
def hill_crypto_route():
    result, error, mode = None, None, None
    matrix_display = None 
    key_mode = 'numeric'
    text_key = ''
    
    if request.method == 'POST':
        try:
            key_mode = request.form.get('keyMode', 'numeric')
            text_key = request.form.get('textKey', '')
            size = request.form.get('size')
            matrix_text = request.form.get('matrix')
            text = request.form.get('text')
            
            matrix = hill_cipher.parse_square_matrix(matrix_text, size)
            matrix_display = matrix 
            
            if 'encrypt' in request.form:
                result = hill_cipher.encrypt_hill(text, matrix)
                mode = "Ciphertext"
            elif 'decrypt' in request.form:
                result = hill_cipher.decrypt_hill(text, matrix)
                mode = "Plaintext"
        except Exception as e: error = str(e)
    
    return render_template('hill_crypto.html', result=result, error=error, mode=mode, key_mode=key_mode, text_key=text_key, matrix_display=matrix_display)

@ex1_bp.route('/hill_matrix', methods=['GET', 'POST'])
def hill_matrix_route():
    results = {}
    error = None
    if request.method == 'POST':
        try:
            size = request.form.get('size')
            matrix = hill_cipher.parse_square_matrix(request.form.get('matrix'), size)
            
            det = hill_cipher.determinant(matrix)
            results['det'] = det
            det_mod = hill_cipher.mod(det)
            results['det_mod'] = det_mod
            trans = hill_cipher.transpose(matrix)
            results['transpose'] = "\n".join(" ".join(str(x) for x in row) for row in trans)

            try:
                crypto_utils.mod_inverse(det_mod, 26)
                results['det_inv'] = crypto_utils.mod_inverse(det_mod, 26)
                inv_m = hill_cipher.inverse_matrix_mod26(matrix)
                results['inverse'] = "\n".join(" ".join(str(x) for x in row) for row in inv_m)
            except ValueError:
                results['det_inv'] = "No Inverse (GCD != 1)"
                results['inverse'] = "Matrix is not invertible mod 26"

        except Exception as e: error = str(e)
    return render_template('hill_matrix.html', results=results, error=error)

@ex1_bp.route('/hill_math', methods=['GET', 'POST'])
def hill_math_route():
    gcd_val, linear_combo, steps, error, mode = None, None, None, None, None
    a_val, b_val, calc_a, calc_b = None, None, None, None

    if request.method == 'POST':
        try:
            a_str = request.form.get('a')
            b_str = request.form.get('b')
            action = request.form.get('action') 

            if not a_str or not b_str: raise ValueError("Please enter both numbers.")
            a = int(a_str)
            b = int(b_str)
            a_val, b_val = a, b
            
            swapped = False
            if b > a:
                calc_a, calc_b = b, a
                swapped = True
            else:
                calc_a, calc_b = a, b
                swapped = False

            g, x, y, calc_steps = crypto_utils.extended_gcd_verbose(calc_a, calc_b)
            gcd_val = g
            steps = calc_steps

            if action == 'gcd':
                mode = 'gcd'
            elif action == 'extended':
                mode = 'extended'
                if swapped: coeff_a, coeff_b = y, x
                else: coeff_a, coeff_b = x, y
                op = "+" if coeff_b >= 0 else "-"
                linear_combo = f"{a_val}({coeff_a}) {op} {b_val}({abs(coeff_b)}) = {g}"

        except Exception as e: error = str(e)
        
    return render_template('hill_math.html', gcd=gcd_val, steps=steps, linear_combo=linear_combo, error=error, a_val=a_val, b_val=b_val, calc_a=calc_a, calc_b=calc_b, mode=mode)

@ex1_bp.route('/primitive_root', methods=['GET', 'POST'])
def primitive_root_route():
    roots_str, error, n_val, steps_log = None, None, None, None
    if request.method == 'POST':
        try:
            n_str = request.form.get('n')
            if not n_str: raise ValueError("Please enter a number.")
            n_val = int(n_str)
            if n_val > 100: raise ValueError("For detailed step display, please keep N <= 100.")
            info = primitive_root.get_primitive_roots_info(n_val, show_steps=True)
            
            if info['roots']: roots_str = ", ".join(str(r) for r in info['roots'])
            else: roots_str = "None found"
            steps_log = info.get('steps', [])
        except Exception as e: error = str(e)
    return render_template('primitive_root.html', roots=roots_str, error=error, n_val=n_val, steps_log=steps_log)