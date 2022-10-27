# update google results to table 'realnames' where missing

import sqlite3
import crawler

NAMES_TO_UPDATE = 10  # how many db entries should be checked and updated?

# initiate db connection
con = sqlite3.connect('names.db')
con.row_factory = lambda cursor, row: row[0] # returns lists instead of tuples for a row
cur = con.cursor()

myquery = ("SELECT name FROM 'realnames' WHERE freq_google IS NULL;")
cur.execute(myquery)
list_of_names_to_check = cur.fetchall()

print(f"{len(list_of_names_to_check)} names with missing Google data, checking {NAMES_TO_UPDATE} of them... ")

for name in list_of_names_to_check[0:NAMES_TO_UPDATE]:
    # check
    res = crawler.get_google_at_matches(name)
    print(name, res)
    # write to db
    q = (f"UPDATE 'realnames' SET freq_google = {res} WHERE name = '{name}';")
    cur.execute(q)
    con.commit()
