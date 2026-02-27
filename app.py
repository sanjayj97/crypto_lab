# app.py
from flask import Flask, render_template, redirect, url_for
from exercise1 import ex1_bp 
from exercise2 import ex2_bp

app = Flask(__name__)

app.register_blueprint(ex1_bp, url_prefix='/ex1')
app.register_blueprint(ex2_bp, url_prefix='/ex2')

@app.route('/')
def root():
    return redirect(url_for('exercise', ex_id='ex1'))

@app.route('/dashboard/<ex_id>')
def exercise(ex_id):
    valid_ex = [f'ex{i}' for i in range(1, 8)]
    if ex_id not in valid_ex:
        return redirect(url_for('exercise', ex_id='ex1'))
    
    return render_template('index.html', active_ex=ex_id)

if __name__ == '__main__':
    app.run(debug=True)