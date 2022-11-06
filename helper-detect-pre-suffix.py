# check table 'realname' against 'prefixes' and 'suffixes' to spot missing entries

import sqlite3

# initiate db connection
con = sqlite3.connect('names.db')
con.row_factory = lambda cursor, row: row[0]  # returns lists instead of tuples for a row
cur = con.cursor()

query1 = ("SELECT name FROM 'realnames' ORDER BY name ASC")
cur.execute(query1)
list_of_realnames = cur.fetchall()

query2 = ("SELECT prefix FROM 'prefixes' ORDER BY prefix ASC")
cur.execute(query2)
list_of_prefixes = cur.fetchall()

query3 = ("SELECT suffix FROM 'suffixes' ORDER BY suffix ASC")
cur.execute(query3)
list_of_suffixes = cur.fetchall()

print(f"{len(list_of_realnames)} realnames, {len(list_of_prefixes)} prefixes ")


# Below functions indicate, where more names should be generated into 'realnames'

def list_unused_suffixes() -> list:
    list = []
    print("\nCheck: All suffixes, which are not yet part of 'realnames': ")
    for suffix in list_of_suffixes:

        result = any(suffix in word for word in list_of_realnames)
        if result is False: list.append(suffix)
    return list


def list_unused_prefixes() -> list:
    list = []
    print("\nCheck: All prefixes, which are not yet part of 'realnames': ")
    for prefix in list_of_prefixes:

        result = any(prefix in word for word in list_of_realnames)
        if result is False: list.append(prefix)
    return list


# Below functions auto-complete column 'prefix'/'suffix' of table 'realnames'

def autocomplete_prefixes():
    print("\nWrite to database: Populate prefixes to 'realnames': ")
    for prefix in list_of_prefixes:

        # using startswith
        result = list(filter(lambda x: x.startswith(prefix), list_of_realnames))
        print(prefix, ':', result)
        for r in result:
            q = (f"UPDATE 'realnames' SET prefix = '{prefix}' WHERE name = '{r}';")
            cur.execute(q)
    con.commit()


def autocomplete_suffixes():
    print("\nWrite to database: Populate suffixes to 'realnames': ")
    for suffix in list_of_suffixes:
        # using in
        result = list(filter(lambda x: suffix in x, list_of_realnames))
        print(suffix, ':', result)
        for r in result:
            q = (f"UPDATE 'realnames' SET suffix = '{suffix}' WHERE name = '{r}';")
            cur.execute(q)
    con.commit()


def list_NULL_NULL_realnames() -> list:
    print("\nCheck for realnames where both prefix and suffix is NULL: ")
    query4 = ("SELECT name FROM 'realnames' WHERE prefix IS NULL and suffix IS NULL;")
    cur.execute(query4)
    list_of_realnames_null = cur.fetchall()
    print(len(list_of_realnames_null), "entries found: ")
    return list_of_realnames_null


if __name__ == "__main__":
    print(list_unused_prefixes())
    print(list_unused_suffixes())
    print(list_NULL_NULL_realnames())
    # autocomplete_suffixes()
    # autocomplete_prefixes()
