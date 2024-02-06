from app import app
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

@app.route('/1')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/', methods=['GET', 'POST'])
def display_stocks():
    if request.method == 'POST':
        # Get form data
        stock_id = request.form['stock_id']
        action = request.form['action'] # Action: add or subtract
        amount = float(request.form['amount'])
        new_amount = request.form['amount']

        # Connect to the SQLite database
        conn = sqlite3.connect('stocks.db')
        c = conn.cursor()

        # Retrieve current price of the stock
        c.execute('SELECT volume FROM stocks WHERE prod_id = ?', (stock_id,))
        current_volume = c.fetchone()[0]

        # Update stock price based on action (add or subtract)
        if action == 'add':
            new_volume = current_volume + amount
        elif action == 'subtract':
            new_volume = current_volume - amount

        c.execute('SELECT volume FROM stocks WHERE prod_id = ?', (stock_id,))
        old_amount = c.fetchone()[0]

        # Update stock price in the database
        c.execute('UPDATE stocks SET volume = ? WHERE prod_id = ?', (new_volume, stock_id))
        
        c.execute('INSERT INTO price_history (prod_id, old_amount, new_amount, add_amount) VALUES (?, ?, ?, ?)', (stock_id, old_amount, new_amount, new_volume))

        conn.commit()
        conn.close()

        # Redirect to the homepage after updating
        return redirect(url_for('display_stocks'))

    # Connect to the SQLite database
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()

    # Retrieve stock information from the database
    c.execute('SELECT * FROM stocks')
    stocks = c.fetchall()

    price_history = {}
    for stock in stocks:
        stock_id = stock[0]
        c.execute('SELECT date(changed_at) as day, old_amount, new_amount, changed_at FROM price_history WHERE prod_id = ? ORDER BY day DESC, changed_at DESC', (stock_id,))
        price_history[stock_id] = c.fetchall()

    # Close the database connection
    conn.close()

    # Render the template with stock information
    return render_template('stocks.html', stocks=stocks, price_history=price_history)

@app.route('/data/<int:prod_id>', methods=['GET'])
def price_history(prod_id):
 

    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()

    # Retrieve price history for the specified stock ID
    c.execute('SELECT * FROM price_history WHERE prod_id = ? ORDER BY changed_at DESC', (prod_id,))
    price_history = c.fetchall()

    # Retrieve stock information for display
    c.execute('SELECT name ,volume FROM stocks WHERE prod_id = ?', (prod_id,))
    stock_info = c.fetchone()

    conn.close()

    return render_template('price_history.html', price_history=price_history, stock_info=stock_info)

@app.route('/disp', methods=['GET', 'POST'])
def disp_stocks():
    error_message = request.args.get('error_message')
    stock_map = {1: 'Diesel', 2: '95'}
    if request.method == 'POST':
        # Get form data
        disp_id = request.form['disp_id']
        p_id = request.form['p_id']
        new_price = float(request.form['new_price'])
        action = request.form['action'] # Action: add or subtract   
        diff = request.form['new_price']

        
 
        # Update stock price in the database
        conn = sqlite3.connect('stocks.db')
        c = conn.cursor()

        c.execute('SELECT sta_met FROM retail WHERE disp_id = ?', (disp_id,))
        old = c.fetchone()[0]    
     
        if action == 'add':
            diff = old + new_price
        elif action == 'subtract':
            diff = new_price - old 

        c.execute('SELECT sta_met FROM retail WHERE disp_id = ?', (disp_id,))
        old_amount = c.fetchone()[0]
        
        if new_price <= old_amount:
            error_message = "New price must be greater than the old amount."
            return redirect(url_for('disp_stocks', error_message=error_message)) 
        
        c.execute('UPDATE retail SET sta_met = ? ,dif = ? WHERE disp_id = ?', (new_price, diff, disp_id))
       
        c.execute('UPDATE  retail SET new_met = ? WHERE disp_id = ?',(old_amount, disp_id) )
       # Insert into price history
        c.execute('INSERT INTO ret_history (disp_id, old_amount, new_amount, diff) VALUES (?, ?, ?, ?)', (disp_id, old_amount, new_price, diff))

        conn.commit()
        conn.close()

        # Redirect to the homepage after updating
        return redirect(url_for('disp_stocks'))
    
    # Connect to the SQLite database
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()

       

    # Retrieve stock information from the database
    c.execute('SELECT disp_id, prod_id, new_met, sta_met FROM retail')
    stocks = c.fetchall()

    # Close the database connection
    conn.close()

    # Render the template with stock information
    return render_template('daily.html', stocks=stocks, error_message=error_message, stock_map=stock_map)

if __name__ == '__main__':
    app.run(debug=True)