import psycopg2
import requests
import json
from flask import Flask, request
from datetime import timedelta
from config import *
from helpers import *

app = Flask(__name__)

db_conn = psycopg2.connect(DATABASE_URI)
cur = db_conn.cursor()

@app.route('/rates', methods=['GET', 'POST'])
def rates():
    # Task 1, Part 1 GET /rates request
    if request.method == 'GET':
        try:
            if not request.args:
                return json.dumps({'message': 'No parameters provided. Please provide date_from, date_to, origin and destination query parameters to return proper results.'}), 400
            date_from = request.args.get('date_from') if 'date_from' in request.args else None
            date_to = request.args.get('date_to') if 'date_to' in request.args else None
            origin = request.args.get('origin').lower() if 'origin' in request.args else None
            destination = request.args.get('destination').lower() if 'destination' in request.args else None
            error = []
            if origin:
                region_slugs = regions(origin, cur)
                port_codes = ports(origin, cur)
                port_code = port(origin, cur)
                if not (region_slugs or port_codes or port_code):
                    return json.dumps({"message": f"{request.args.get('origin')} is invalid. Please enter a valid port code or region_slug."}), 404
            
            if destination:
                region_slugs = regions(destination, cur)
                port_codes = ports(destination, cur)
                port_code = port(destination, cur)
                if not (region_slugs or port_codes or port_code):
                    return json.dumps({"message": f"{request.args.get('destination')} is invalid. Please enter a valid port code or region_slug."}), 404

            if date_from and date_to:
                start = convert_date(date_from)
                end = convert_date(date_to)
                if start > end:
                    return json.dumps({"message": "date_from should be less than or equal to date_to."}), 400
            
            if date_from and date_to and origin and destination is not None:
                cur.execute('''SELECT CAST(day AS text) AS day, 
                            CAST(AVG(price) AS int) AS average_price FROM prices 
                            WHERE (LOWER(orig_code) = %s OR 
                            orig_code in (select code from ports where parent_slug = %s) OR
                            orig_code in (select code from ports where parent_slug in 
                            (select slug from regions where regions.parent_slug =%s))) 
                            AND (LOWER(dest_code) = %s OR 
                            dest_code in (select code from ports where parent_slug = %s) OR
                            dest_code in (select code from ports where parent_slug in 
                            (select slug from regions where regions.parent_slug =%s)))  
                            AND day BETWEEN %s AND %s
                            GROUP BY day ORDER BY day;''',
                            (origin, origin, origin, destination, destination, destination, date_from, date_to))
                response = result_arr(cur)
                return response, 200

            if date_from in (None, ''):
                error.append("date_from")
            if date_to in (None, ''):
                error.append("date_to")
            if origin in (None, ''):
                error.append("origin")
            if destination in (None, ''):
                error.append("destination")
            if date_from or date_to or origin or destination is None:
                return json.dumps({"message": f"{error} param/s missing."}), 400

        except Exception as e:
            return json.dumps({"message": str(e)}), 500

    # Task 1, Part 1 (including Part 2) POST /rates request
    if request.method == 'POST':
        try:
            if request.json is None:
                return json.dumps({'message': 'No input data provided'}), 400
            date_from = request.json['date_from'] if 'date_from' in request.json else None
            date_to = request.json['date_to'] if 'date_to' in request.json else None
            orig_code = request.json['origin_code'].upper() if 'origin_code' in request.json else None
            dest_code = request.json['destination_code'].upper() if 'destination_code' in request.json else None
            price = int(request.json['price']) if 'price' in request.json else None
            currency = request.json['currency'].upper() if 'currency' in request.json else None
            data = []
            error = []

            # if currency key is available in json, Part 2 of Task 2
            if currency:
                response = requests.get(CONVERT_URL).json()
                currencies = response["rates"]
                if currency in currencies:
                    price = int(price / currencies[currency])   # convert to USD 
                else:
                    return json.dumps({"message": f"Invalid currency: {request.json['currency']}. Please provide a valid 3 letter currency code."}), 400

            if date_from and date_to and orig_code and dest_code and price:
                start = convert_date(date_from)
                end = convert_date(date_to)
                if start > end:
                    return json.dumps({"message": "date_from should be less than or equal to date_to."}), 400
                delta = end - start
                for i in range(delta.days + 1):
                    day = start + timedelta(days=i)
                    data.append({'orig_code': orig_code, 'dest_code': dest_code, 'day': day, 'price': price})
                query = '''INSERT INTO prices (orig_code, dest_code, day, price) 
                            VALUES (%(orig_code)s, %(dest_code)s, %(day)s, %(price)s);'''
                cur.executemany(query, data)
                db_conn.commit()
                return json.dumps({"message": f"{cur.rowcount} row/s added.", "data": f"{data}"}), 201
            
            if date_from in (None, ''):
                error.append("date_from")
            if date_to in (None, ''):
                error.append("date_to")
            if orig_code in (None, ''):
                error.append("origin_code")
            if dest_code in (None, ''):
                error.append("destination_code")
            if price in (None, ''):
                error.append("price")
            if currency is '':
                error.append("currency")
            if date_from or date_to or orig_code or dest_code or price or currency is None:
                return json.dumps({"message": f"{error} data missing."}), 400
        
        except Exception as e:
            db_conn.rollback()
            return json.dumps({"message": str(e)}), 500


# Task 1, Part 2 GET /rates_null request
@app.route('/rates_null', methods=['GET'])
def rates_null():
    try:
        if not request.args:
            return json.dumps({'message': 'No parameters provided. Please provide date_from, date_to, origin and destination query parameters to return proper results.'}), 400
        date_from = request.args.get('date_from') if 'date_from' in request.args else None
        date_to = request.args.get('date_to') if 'date_to' in request.args else None
        origin = request.args.get('origin').lower() if 'origin' in request.args else None
        destination = request.args.get('destination').lower() if 'destination' in request.args else None
        error = []
        if origin:
            region_slugs = regions(origin, cur)
            port_codes = ports(origin, cur)
            port_code = port(origin, cur)
            if not (region_slugs or port_codes or port_code):
                return json.dumps({"message": f"{request.args.get('origin')} is invalid. Please enter a valid port code or region_slug."}), 404
        
        if destination:
            region_slugs = regions(destination, cur)
            port_codes = ports(destination, cur)
            port_code = port(destination, cur)
            if not (region_slugs or port_codes or port_code):
                return json.dumps({"message": f"{request.args.get('destination')} is invalid. Please enter a valid port code or region_slug."}), 404

        if date_from and date_to:
            start = convert_date(date_from)
            end = convert_date(date_to)
            if start > end:
                return json.dumps({"message": "date_from should be less than or equal to date_to."}), 400
        
        if date_from and date_to and origin and destination is not None:
            cur.execute('''SELECT CAST(day AS text) AS day, 
                            CASE WHEN COUNT(*) < 3 THEN null
                            ELSE CAST(AVG(price) AS int)
                            END AS average_price FROM prices
                            WHERE (LOWER(orig_code) = %s OR 
                            orig_code in (select code from ports where parent_slug = %s) OR
                            orig_code in (select code from ports where parent_slug in 
                            (select slug from regions where regions.parent_slug =%s))) 
                            AND (LOWER(dest_code) = %s OR 
                            dest_code in (select code from ports where parent_slug = %s) OR
                            dest_code in (select code from ports where parent_slug in 
                            (select slug from regions where regions.parent_slug =%s)))  
                            AND day BETWEEN %s AND %s
                            GROUP BY day ORDER BY day;''',
                            (origin, origin, origin, destination, destination, destination, date_from, date_to))
            response = result_arr(cur)
            return response, 200

        if date_from in (None, ''):
            error.append("date_from")
        if date_to in (None, ''):
            error.append("date_to")
        if origin in (None, ''):
            error.append("origin")
        if destination in (None, ''):
            error.append("destination")
        if date_from or date_to or origin or destination is None:
            return json.dumps({"message": f"{error} param/s missing."}), 400

    except Exception as e:
        return json.dumps({"message": str(e)}), 500


if __name__ == '__main__':
   app.run(debug=True)