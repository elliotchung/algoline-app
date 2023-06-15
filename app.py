from flask import Flask, render_template, url_for, request, redirect, flash, session
import psycopg2
from datetime import datetime
import config
import AlgoLine
import json

app = Flask(__name__, static_url_path='/static')

def get_db_conn():
    conn = psycopg2.connect(
        host=config.DB_HOST,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASS
    )
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form.get('ticker')
    else:
        ticker = 'SPY'

    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute(f"SELECT id, name FROM stock WHERE symbol = '{ticker}';")
    result = cur.fetchall()
    if len(result) == 0:
        cur.close()
        conn.close()
        return render_template('index.html', desc='No such ticker', ticker=ticker, rows=[])
    
    stock_id = result[0][0]
    desc = result[0][1]

    #5 min price chart
    cur.execute(f"SELECT * FROM stock_price WHERE stock_id = {stock_id} ORDER BY dt asc;")
    rows = cur.fetchall()
    for index, row in enumerate(rows):
        row = list(row)
        rows[index] = row
    for row in rows:
        row[1] = row[1].timestamp()
        row[2] = float(row[2])
        row[3] = float(row[3])
        row[4] = float(row[4])
        row[5] = float(row[5])
        row[6] = int(row[6])

    #daily price chart
    cur.execute(f"SELECT dt, open, high, low, close, volume, AVG(volume) OVER (ORDER BY dt ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) AS vol_50 FROM daily_stock_price WHERE stock_id = {stock_id} ORDER BY dt ASC;")
    daily_rows = cur.fetchall()
    for index, row in enumerate(daily_rows):
        row = list(row)
        daily_rows[index] = row
    for row in daily_rows:
        row[0] = datetime.combine(row[0], datetime.min.time()).timestamp()
        row[1] = float(row[1])
        row[2] = float(row[2])
        row[3] = float(row[3])
        row[4] = float(row[4])
        row[5] = int(row[5])
        row[6] = int(row[6])

    cur.execute(f"select time_bucket(INTERVAL '1 day', dt) AS bucket, first(open, dt), max(high), min(low), last(close, dt), SUM(volume) as total_volume from stock_price where stock_id = {stock_id} group by bucket order by bucket ASC;")
    daily_rows_2 = cur.fetchall()

    for index, row in enumerate(daily_rows_2):
        row = list(row)
        daily_rows_2[index] = row
    for row in daily_rows_2:
        row[0] = datetime.combine(row[0], datetime.min.time()).timestamp()
        row[1] = float(row[1])
        row[2] = float(row[2])
        row[3] = float(row[3])
        row[4] = float(row[4])
        row[5] = int(row[5])
    daily_rows = daily_rows + daily_rows_2
    cur.close()
    conn.close()

    low_trendlines_final, high_trendlines_final = AlgoLine.create_trendlines(ticker)

    return render_template('index.html', desc=desc, ticker=ticker, rows=rows, daily_rows=daily_rows, low_trendlines_final=low_trendlines_final, high_trendlines_final=high_trendlines_final)

if __name__ == '__main__':
    app.run(debug=True)