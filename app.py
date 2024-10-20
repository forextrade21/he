from flask import Flask, render_template, request, redirect, url_for # type: ignore
import os
from werkzeug.utils import secure_filename # type: ignore

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Trade data (Temporary storage)
open_trades = []
closed_trades = []

# Index route (Homepage)
@app.route('/')
def index():
    return render_template('index.html', open_trades=open_trades, closed_trades=closed_trades)

# Add trade route
@app.route('/add_trade', methods=['POST'])
def add_trade():
    day = request.form['day']
    month = request.form['month']
    year = request.form['year']
    pair = request.form['pair']
    bias = request.form['bias']
    outcome = request.form['outcome']
    profit_loss = request.form['profit_loss']
    entry_price = request.form['entry_price']
    exit_price = request.form['exit_price']
    
    # Handle image upload
    trade_image = request.files['trade_image']
    if trade_image:
        filename = secure_filename(trade_image.filename)
        trade_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        filename = None

    # Create trade dictionary
    trade = {
        'day': day,
        'month': month,
        'year': year,
        'pair': pair,
        'bias': bias,
        'outcome': outcome,
        'profit_loss': profit_loss,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'image': filename
    }
    open_trades.append(trade)

    return redirect(url_for('index'))

# Close trade route
@app.route('/close_trade/<int:trade_id>', methods=['POST'])
def close_trade(trade_id):
    trade = open_trades.pop(trade_id)
    closed_trades.append(trade)
    return redirect(url_for('index'))

# Edit trade route
@app.route('/edit_trade/<int:trade_id>', methods=['GET', 'POST'])
def edit_trade(trade_id):
    trade = open_trades[trade_id]

    if request.method == 'POST':
        trade['profit_loss'] = request.form['profit_loss']
        trade['exit_price'] = request.form['exit_price']
        
        # Handle new image upload (if any)
        trade_image = request.files['trade_image']
        if trade_image:
            filename = secure_filename(trade_image.filename)
            trade_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            trade['image'] = filename

        return redirect(url_for('index'))

    return render_template('edit_trade.html', trade=trade, trade_id=trade_id)

if __name__ == '__main__':
    app.run(debug=True)
