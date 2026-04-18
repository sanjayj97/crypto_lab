# exercise4/routes.py

from flask import render_template, request
from . import ex4_bp
from . import md5_logic
from . import cmac_logic

@ex4_bp.route('/md5', methods=['GET', 'POST'])
def md5_route():
    result_hash = None
    input_text = None
    error = None
    log_steps = None

    if request.method == 'POST':
        try:
            input_text = request.form.get('text', '')
            input_bytes = input_text.encode('utf-8')
            result_hash, log_steps = md5_logic.md5_hash(input_bytes)
        except Exception as e:
            error = f"An unexpected calculation error occurred: {str(e)}"

    return render_template('md5.html', 
                           result=result_hash, 
                           input_text=input_text, 
                           error=error,
                           log_steps=log_steps)


@ex4_bp.route('/cmac', methods=['GET', 'POST'])
def cmac_route():
    result_tag = None
    input_key = None
    input_message = None
    input_truncate_len = None
    error = None
    log_steps = None

    if request.method == 'POST':
        try:
            input_key = request.form.get('key', '').strip()
            input_message = request.form.get('message', '')
            input_truncate_len = request.form.get('truncate_len', '').strip()
            
            truncate_len = None
            if input_truncate_len:
                try:
                    truncate_len = int(input_truncate_len)
                    if not (1 <= truncate_len <= 16):
                        raise ValueError("Truncation length must be an integer between 1 and 16.")
                except (ValueError, TypeError):
                    raise ValueError("Truncation length must be a valid integer.")

            if len(input_key) != 32:
                raise ValueError(f"Key must be exactly 32 hex characters. Received {len(input_key)} characters.")
            key_bytes = bytes.fromhex(input_key)

            message_bytes = input_message.encode('utf-8')
            tag_bytes, log_steps = cmac_logic.cmac(key_bytes, message_bytes, truncate_len=truncate_len) 
            result_tag = tag_bytes.hex()
            
        except ValueError as e: 
            error = str(e)
        except Exception as e:
            error = f"An unexpected calculation error occurred: {str(e)}"

    return render_template('cmac.html', 
                           result=result_tag, 
                           input_key=input_key, 
                           input_message=input_message, 
                           input_truncate_len=input_truncate_len,
                           error=error,
                           log_steps=log_steps)