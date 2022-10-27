# update google results to table 'realnames' where missing

import sqlite3
import crawler

# initiate db connection
con = sqlite3.connect('names.db')
con.row_factory = lambda cursor, row: row[0] # returns lists instead of tuples for a row
cur = con.cursor()

myquery = ("SELECT name FROM 'realnames' WHERE freq_google IS NULL;")
cur.execute(myquery)
list_of_names_to_check = cur.fetchall()

for name in list_of_names_to_check[0:10]:
    # check
    res = crawler.get_google_at_matches(name)
    print(name, res)
    # write to db
    q = (f"UPDATE 'realnames' SET freq_google = {res} WHERE name = '{name}';")
    cur.execute(q)
    con.commit()
