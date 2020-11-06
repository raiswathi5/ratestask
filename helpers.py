import json
from datetime import datetime

def convert_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def port(code, cur):
    cur.execute('''SELECT code FROM ports WHERE LOWER(code) = %s;''', (code,))
    return cur.fetchall()

def ports(code, cur):
    cur.execute('''SELECT code FROM ports WHERE parent_slug = %s;''', (code,))
    return cur.fetchall()

def regions(code, cur):
    cur.execute('''SELECT slug FROM regions WHERE parent_slug = %s;''', (code,))
    return cur.fetchall()

def result_arr(cur):
    row_headers=[x[0] for x in cur.description]
    values = cur.fetchall()
    json_data=[]
    for value in values:
        json_data.append(dict(zip(row_headers,value)))
    return json.dumps(json_data)