from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Trade data storage
open_trades = []
closed_trades = []

def get_db_connection():
    # الحصول على عنوان IP الخاص بالعميل
    client_ip = request.remote_addr
    db_name = f"trading_journal_{client_ip}.db"
    
    conn = sqlite3.connect(db_name)
    conn.execute('CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, day_name TEXT, day INTEGER, month_name TEXT, month INTEGER, year INTEGER, pair TEXT, bias TEXT, outcome TEXT, profit_loss TEXT, entry_price REAL, exit_price TEXT, image TEXT)')
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    # جلب البيانات من قاعدة البيانات
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trades WHERE closed = 0')
    open_trades = cursor.fetchall()

    cursor.execute('SELECT * FROM trades WHERE closed = 1')
    closed_trades = cursor.fetchall()

    conn.close()

    return render_template('index.html', open_trades=open_trades, closed_trades=closed_trades)

@app.route('/add_trade', methods=['POST'])
def add_trade():
    day_name = request.form['day_name']
    day = request.form['day']
    month_name = request.form['month_name']
    month = request.form['month']
    year = request.form['year']
    pair = request.form['pair']
    bias = request.form['bias']
    outcome = request.form['outcome']
    profit_loss = request.form['profit_loss'] if request.form['profit_loss'] else 'No'
    entry_price = request.form['entry_price']
    exit_price = request.form['exit_price'] if request.form['exit_price'] else 'No'
    
    # Handling image upload
    trade_image = request.files['trade_image']
    if trade_image:
        filename = secure_filename(trade_image.filename)
        trade_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        filename = None

    # Add trade to the database
    conn = get_db_connection()
    conn.execute('INSERT INTO trades (day_name, day, month_name, month, year, pair, bias, outcome, profit_loss, entry_price, exit_price, image, closed) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                 (day_name, day, month_name, month, year, pair, bias, outcome, profit_loss, entry_price, exit_price, filename, 0))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/close_trade/<int:trade_id>', methods=['POST'])
def close_trade(trade_id):
    conn = get_db_connection()
    conn.execute('UPDATE trades SET closed = 1 WHERE id = ?', (trade_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete_closed_trade/<int:trade_id>', methods=['POST'])
def delete_closed_trade(trade_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM trades WHERE id = ?', (trade_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit_trade/<int:trade_id>', methods=['GET', 'POST'])
def edit_trade(trade_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        profit_loss = request.form['profit_loss'] if request.form['profit_loss'] else 'No'
        exit_price = request.form['exit_price'] if request.form['exit_price'] else 'No'

        # Handling image upload (if a new image is uploaded)
        trade_image = request.files['trade_image']
        if trade_image:
            filename = secure_filename(trade_image.filename)
            trade_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None

        # Update trade in the database
        conn.execute('UPDATE trades SET profit_loss = ?, exit_price = ?, image = ? WHERE id = ?', (profit_loss, exit_price, filename, trade_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    # Fetch the trade details for editing
    cursor.execute('SELECT * FROM trades WHERE id = ?', (trade_id,))
    trade = cursor.fetchone()
    conn.close()

    return render_template('edit_trade.html', trade=trade)

if __name__ == '__main__':
    app.run(debug=True)
