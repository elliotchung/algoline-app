import psycopg2
import config
from datetime import datetime
from findiff import FinDiff
import numpy as np
import json

def get_db_conn():
    conn = psycopg2.connect(
        host=config.DB_HOST,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASS
    )
    return conn

def create_trendlines(ticker):
    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute(f"SELECT id, name FROM stock WHERE symbol = '{ticker}';")
    result = cur.fetchall()
    if len(result) == 0:
        cur.close()
        conn.close()

    stock_id = result[0][0]
    dataDict = {}
    dataDict[stock_id] = []
    volume = []

    #daily price chart
    cur.execute(f"SELECT dt, open, high, low, close, volume, AVG(volume) OVER (ORDER BY dt ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) AS vol_50 FROM daily_stock_price WHERE stock_id = {stock_id} ORDER BY dt ASC;")
    daily_rows = cur.fetchall()
    #append to dataDict with stock_id as key
    for row in daily_rows:
        rowDict = {'date': datetime.combine(row[0], datetime.min.time()).timestamp(), 'open': float(row[1]), 'high': float(row[2]), 'low': float(row[3]), 'close': float(row[4]), 'volume': int(row[5]), 'vol_50': float(row[6])}
        dataDict[stock_id].append(rowDict)
        volume.append(int(row[5]))

    #time bucket
    cur.execute(f"select time_bucket(INTERVAL '1 day', dt) AS bucket, first(open, dt), max(high), min(low), last(close, dt), SUM(volume) as total_volume from stock_price where stock_id = {stock_id} group by bucket order by bucket ASC;")
    daily_rows_2 = cur.fetchall()
    temp_volume = volume[-49:]
    temp_volume_50 = []
    for row in daily_rows_2:
        temp_volume.append(int(row[5]))
    def calculate_moving_average(data, window):
        for i in range(len(data) - window + 1):
            yield sum(data[i:i+window])/window
    temp_volume_50 = list(calculate_moving_average(temp_volume, 50))
    for i in range(len(daily_rows_2)):
        rowDict = {'date': datetime.combine(daily_rows_2[i][0], datetime.min.time()).timestamp(), 'open': float(daily_rows_2[i][1]), 'high': float(daily_rows_2[i][2]), 'low': float(daily_rows_2[i][3]), 'close': float(daily_rows_2[i][4]), 'volume': int(daily_rows_2[i][5]), 'vol_50': float(temp_volume_50[i])}
        dataDict[stock_id].append(rowDict)
    cur.close()
    conn.close()

    #calculate momentum and acceleration
    low = [dataDict[stock_id][i]['low'] for i in range(len(dataDict[stock_id]))]
    high = [dataDict[stock_id][i]['high'] for i in range(len(dataDict[stock_id]))]
    volume = [dataDict[stock_id][i]['volume'] for i in range(len(dataDict[stock_id]))]
    vol_50 = [dataDict[stock_id][i]['vol_50'] for i in range(len(dataDict[stock_id]))]
    dates = [dataDict[stock_id][i]['date'] for i in range(len(dataDict[stock_id]))]

    #find local minima and maxima
    def get_extrema(isMin, arr, mom, acc):
        return [
            i for i in range(len(mom)-1) #Check logic here!!!
            if (acc[i] > 0 if isMin else acc[i] < 0) 
            and(
                (mom[i] == 0) or
                (i != len(mom) - 1 and (mom[i] > 0 and mom[i+1] < 0) and (arr[i] >= arr[i+1])) 
                or (mom[i] < 0 and mom[i+1] > 0 and arr[i] <= arr[i+1])
                or (i != 0 and mom[i-1] > 0 and mom[i] < 0 and arr[i-1] < arr[i])
                or (mom[i-1] < 0 and mom[i] > 0 and arr[i-1] > arr[i])
                )
            ]

    dx = 1 # 1 day
    dydx = FinDiff(0, dx, 1)
    dydx2 = FinDiff(0, dx, 2)

    low_arr = np.asarray(low)
    low_mom = dydx(low_arr)
    low_acc = dydx2(low_arr)

    high_arr = np.asarray(high)
    high_mom = dydx(high_arr)
    high_acc = dydx2(high_arr)

    minima_index = get_extrema(True, low_arr, low_mom, low_acc)
    minima_values = [low_arr[i] for i in minima_index]

    maxima_index = get_extrema(False, high_arr, high_mom, high_acc)
    maxima_values = [high_arr[i] for i in maxima_index]

    high_volume_index = []
    for i in minima_index:
        if volume[i] > vol_50[i]:
            high_volume_index.append(i)

    minima_high_volume_values = [low_arr[i] for i in high_volume_index]
    maxima_high_volume_values = [high_arr[i] for i in high_volume_index]

    #draw trendlines
    #Variables
    max_gradient = 1
    range_pct = 0.1

    def calculate_gradient_intercept(x1, y1, x2, y2):
        # Calculate the gradient (slope)
        M = (y2 - y1) / (x2 - x1)

        # Calculate the intercept
        C = y1 - M * x1

        return M, C

    #Check if gradient is too steep
    def gradient_test(M, max_gradient):
        if abs(M) > max_gradient:
            return False
        else:
            return True

    #check if the line is within the range of the latest price
    def line_dist_test(M, C, last, last_value, range_pct):
        Y = M * last + C
        if last_value * (1 - range_pct) < Y < last_value * (1 + range_pct):
            return True

    #Creates the trendline array for plotting    
    def create_line_array(start, end, gradient, intercept):
        x_array = np.arange(start, end, 1)
        y_array = gradient * x_array + intercept
        return x_array, y_array

    #Check if the trendline cuts through the stock prices
    stock_index_array = [i for i in range(len(low))]
    def line_array_dist_test(isMin, trendline_index, value):
        start_i = stock_index_array.index(trendline_index[0])
        stock_index_array_temp = stock_index_array[start_i:]
        low_temp = low[start_i:]
        high_temp = high[start_i:]
        for i in range(len(stock_index_array_temp)-1): #exclude the last value
            if isMin:
                if value[i] > low_temp[i]:
                    return False
            else:
                if value[i] < high_temp[i]:
                    return False
        return True            

    #Create the trendline dictionary
    low_trendlines_dict = {}
    high_trendlines_dict = {}

    for i in high_volume_index:
        for j in minima_index:
            if j > i:
                M, C = calculate_gradient_intercept(i, minima_high_volume_values[high_volume_index.index(i)], j, minima_values[minima_index.index(j)])
                low_trendlines_dict[(i, j)] = (M, C)

    for i in high_volume_index:
        for j in maxima_index:
            if j > i:
                M, C = calculate_gradient_intercept(i, maxima_high_volume_values[high_volume_index.index(i)], j, maxima_values[maxima_index.index(j)])
                high_trendlines_dict[(i, j)] = (M, C)

    #Filter the trendlines to only include those with gradients that are not too steep
    filtered_gradient_low_trendlines_dict = {}
    filtered_gradient_high_trendlines_dict = {}

    for key, value in low_trendlines_dict.items():
        if gradient_test(value[0], max_gradient):
            filtered_gradient_low_trendlines_dict[key] = value

    for key, value in high_trendlines_dict.items():
        if gradient_test(value[0], max_gradient):
            filtered_gradient_high_trendlines_dict[key] = value


    #Filter the trendlines to only include those that are within the range of the latest price
    filtered_low_trendlines_dict = {}
    filtered_high_trendlines_dict = {}

    for key, value in filtered_gradient_low_trendlines_dict.items():
        if line_dist_test(value[0], value[1], len(dates) - 1, low[-1], range_pct):
            filtered_low_trendlines_dict[key] = value

    for key, value in filtered_gradient_high_trendlines_dict.items():
        if line_dist_test(value[0], value[1], len(dates) - 1, high[-1], range_pct):
            filtered_high_trendlines_dict[key] = value


    #Create the trendline arrays
    low_trendlines_arrays = {}
    high_trendlines_arrays = {}

    for key, value in filtered_low_trendlines_dict.items():
        low_trendlines_arrays[key] = create_line_array(key[0], len(dates), value[0], value[1])

    for key, value in filtered_high_trendlines_dict.items():
        high_trendlines_arrays[key] = create_line_array(key[0], len(dates), value[0], value[1])

    #Filter the trendline arrays to only include those that do not cut through the stock prices
    filtered_low_trendlines_arrays = {}
    filtered_high_trendlines_arrays = {}

    for key, value in low_trendlines_arrays.items():
        if line_array_dist_test(True, value[0], value[1]):
            filtered_low_trendlines_arrays[key] = value

    for key, value in high_trendlines_arrays.items():
        if line_array_dist_test(False, value[0], value[1]):
            filtered_high_trendlines_arrays[key] = value

    #convert arrays to lists
    for key, value in filtered_low_trendlines_arrays.items():
        filtered_low_trendlines_arrays[key] = (value[0].tolist(), value[1].tolist())

    for key, value in filtered_high_trendlines_arrays.items():
        filtered_high_trendlines_arrays[key] = (value[0].tolist(), value[1].tolist())

    #trendline dates
    low_trendlines_final = {}
    high_trendlines_final = {}


    for index, (key, value) in enumerate(filtered_low_trendlines_arrays.items()):
        low_trendlines_final[index] = [[dates[i] for i in value[0]], value[1]]

    for index, (key, value) in enumerate(filtered_high_trendlines_arrays.items()):
        high_trendlines_final[index] = [[dates[i] for i in value[0]], value[1]]

    low_trendlines_list = []
    high_trendlines_list = []

    for value in low_trendlines_final.values():
        temp_list = []
        for i in range(len(value[0])):
            temp_list.append({'value': value[1][i], 'time': value[0][i]})
        low_trendlines_list.append(temp_list)

    for value in high_trendlines_final.values():
        temp_list = []
        for i in range(len(value[0])):
            temp_list.append({'value': value[1][i], 'time': value[0][i]})
        high_trendlines_list.append(temp_list)

    #convert to json
    low_trendlines_json = json.dumps(low_trendlines_list)
    high_trendlines_json = json.dumps(high_trendlines_list)

    return low_trendlines_json, high_trendlines_json