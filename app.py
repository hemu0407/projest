import mysql.connector
from flask import Flask, render_template, request, redirect, session
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

db = mysql.connector.connect(
    host="localhost",
    user="your_user",
    password="your_password",
    database="your_database"
)
cursor = db.cursor()

@app.route('/')
def home():
    news_api_key = "your_news_api_key"
    news_url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={news_api_key}"
    news_response = requests.get(news_url).json()
    news_articles = news_response.get("articles", [])

    user = session.get('user')

    return render_template('home.html', news_articles=news_articles, user=user)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        return redirect('/')
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            session['user'] = username
            return redirect('/')
        else:
            return "Invalid credentials!"
    return render_template('signin.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/stocks')
def stocks():
    stock_data = [
        {"symbol": "AAPL", "price": 178.99, "change": "+1.25%"},
        {"symbol": "GOOGL", "price": 2801.12, "change": "-0.5%"},
        {"symbol": "TSLA", "price": 799.34, "change": "+2.8%"}
    ]
    return render_template('stocks.html', stock_data=stock_data)

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/signin')

    username = session['user']
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user_data = cursor.fetchone()

    return render_template('profile.html', user_data=user_data)

@app.route('/buy', methods=['POST'])
def buy_stock():
    if 'user' not in session:
        return redirect('/signin')

    stock_symbol = request.form['stock_symbol']
    quantity = int(request.form['quantity'])
    username = session['user']

    cursor.execute("INSERT INTO transactions (username, stock_symbol, quantity, type) VALUES (%s, %s, %s, 'buy')",
                   (username, stock_symbol, quantity))
    db.commit()

    return redirect('/portfolio')

@app.route('/portfolio')
def portfolio():
    if 'user' not in session:
        return redirect('/signin')

    username = session['user']
    cursor.execute("SELECT stock_symbol, SUM(quantity) FROM transactions WHERE username = %s GROUP BY stock_symbol",
                   (username,))
    portfolio_data = cursor.fetchall()

    return render_template('portfolio.html', portfolio_data=portfolio_data)

if __name__ == '__main__':
    app.run(debug=True)
