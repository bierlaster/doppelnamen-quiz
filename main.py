#!/usr/bin/env python

''' Doppelnamen-Quiz ----------------------
    Generate random Doppelnamen and check, if they really exist in Austria

    Set desired mode in line 20:
    # MODE 1: Generate x random Doppelnamen with their actual frequency
    # MODE 2: Check user input for authenticity - warning: any user input is written to database!
    # MODE 3: Interactive quiz mode

'''

import sqlite3
import random
import logging
import pprint
from colorama import init, Fore
import crawler  # own

MODE = ''  # valid: [1, 2, 3, ''] -- leave empty for terminal user prompt
mode_dict = {
    1: 'MODE 1: Generate n random Doppelnamen (and check their actual frequency)',
    2: 'MODE 2: Check user input for authenticity - warning: any user input is written to database!',
    3: 'MODE 3: Interactive quiz mode'
}

# logging.basicConfig(encoding='utf-8', level=logging.INFO) # filename='example.log',


# init
pp = pprint.PrettyPrinter(indent=4)
init()  # colorama

# disable randomness by setting a static seed (instead of system time based)
# random.seed(10)  # WARNING: REMOVE IN PRODUCTION !

# initiate db connection
con = sqlite3.connect('names.db')
cur = con.cursor()

# select prefixes
myquery = ("SELECT prefix, frequency FROM 'prefixes';")
cur.execute(myquery)
prefix_tuples = cur.fetchall()
prefix_list_weighted = []
for prefix, freq in prefix_tuples:
    for i in range(freq):
        prefix_list_weighted.append(prefix)

logging.info(f"OK: {len(prefix_tuples)} rows selected from 'prefixes'")


# select suffixes
myquery = ("SELECT suffix, frequency FROM 'suffixes';")
cur.execute(myquery)
suffix_tuples = cur.fetchall()
suffix_list_weighted = []
for suffix, freq in suffix_tuples:
    for i in range(freq):
        suffix_list_weighted.append(suffix)
logging.info(f"OK: {len(suffix_tuples)} rows selected from 'suffixes'")


# select real Doppelnamen
myquery = ("SELECT name, freq_adler, freq_herold, freq_abc, freq_google FROM 'realnames';")
cur.execute(myquery)
realname_tuples = cur.fetchall()
realname_list = [x[0] for x in realname_tuples]
realname_dict = {}
for name, freq_adler, freq_herold, freq_abc, freq_google in realname_tuples:
    realname_dict[name] = {
        'freq_adler': freq_adler,
        'freq_herold': freq_herold,
        'freq_abc': freq_abc,
        'freq_google': freq_google
    }
logging.info(f"OK: {len(realname_list)} rows selected from 'realnames'")


# select fakenames
myquery = ("SELECT name, freq_herold, freq_abc FROM 'fakenames';")
cur.execute(myquery)
fakename_tuples = cur.fetchall()
fakename_list = [x[0] for x in fakename_tuples]
fakename_dict = {}
logging.info(f"OK: {len(fakename_list)} rows selected from 'fakenames'")



def generate_doppelname_simple() -> tuple[str, bool]:
    ''' :returns a Doppelname (string) with a true/false (bool) flag '''

    name = random.choice(prefix_list_weighted) + random.choice(suffix_list_weighted)
    if name in realname_list:
        return name, True
    else:
        return name, False

def generate_doppelname_w_freq(name='') -> dict:
    ''' :returns a Doppelname with its frequency in serval databases
    '''
    # generate if no input is given
    if name == '':
        name = random.choice(prefix_list_weighted) + random.choice(suffix_list_weighted)

    # if confirmed real name: return frequencies
    if [item for item in realname_tuples if item[0] == name]:
        d = {'name': name,
             'realname': True,
             'freq_adler': realname_dict[name]['freq_adler'],
             'freq_herold': realname_dict[name]['freq_herold'],
             'freq_abc': realname_dict[name]['freq_abc'],
             'freq_google': realname_dict[name]['freq_google'],
             }
        return d

    # else check 'fakenames' table
    else:
        # if checked and confirmed fake, return result
        if [item for item in fakename_tuples if item[0] == name]:
            d = {'name': name,
                 'realname': False
                 }
            return d

        # if not yet checked, check now
        else:
            logging.info(f"Crawling herold & abc for '{name}'")
            v_h = crawler.get_herold_telefonbuch_matches(name)
            v_a = crawler.get_telefonabc_matches(name)

            if v_h == 0 and v_a == 0:
                # add to 'fakenames' table
                q = (f"INSERT INTO fakenames (name, freq_herold, freq_abc) VALUES ('{name}', 0, 0); ")
                cur.execute(q)
                con.commit()
                d = {'name': name,
                     'realname': False
                     }
                return d

            else:
                logging.info(f"Crawling google for '{name}'")
                v_g = crawler.get_google_at_matches(name)

                # add to 'realnames' table
                # if
                if v_g is None:
                    q = (f"INSERT INTO realnames (name, freq_herold, freq_abc) VALUES ('{name}', {v_h}, {v_a}); ")
                else:
                    q = (f"INSERT INTO realnames (name, freq_herold, freq_abc, freq_google) VALUES ('{name}', {v_h}, {v_a}, {v_g}); ")
                cur.execute(q)
                con.commit()
                d = {'name': name,
                     'realname': True,
                     'freq_abc': v_a,
                     'freq_herold': v_h,
                     'freq_google': v_g
                     }
                return d


if __name__ == "__main__":
    logging.info(f"MODE {MODE}")
    logging.info(f"Dataset: \n"
                 f"{len(prefix_tuples)} prefixes x {len(suffix_tuples)} suffixes = {(len(prefix_tuples) * len(suffix_tuples))} name combinations \n"
                 f"{len(realname_list)} confirmed Doppelnamen, {len(fakename_list)} confirmed fake names")

    if MODE == '':
        print("\nDOPPELNAME is available in 3 modes: ")
        for s in mode_dict.values():
            print(" ",s)
        MODE = int(input(f"\nPlease select mode:  "))

    if MODE == 1:
        # MODE 1: Generate x random Doppelnamen ---------------------
        while True:
            u_rounds = int(input(f"\nHow many names should be generated (e.g. 5) "))
            for i in range(u_rounds):
                pp.pprint(generate_doppelname_w_freq())


    elif MODE == 2:
        # MODE 2: Check user input for authenticity ---------------------
        while True:
            u_value = input(f"\nWhich Doppelname do you want to check? ")
            pp.pprint(generate_doppelname_w_freq(u_value))


    elif MODE == 3:
        # MODE 3: interactive quiz mode ---------------------
        score = 0
        quiz_pool = []  # list of dicts
        valid_responses = ['r', 'R', 'real', 'Real', 'f', 'F', 'fake', 'Fake']

        u_rounds = int(input(f"\nHow many quiz rounds do you want to play? (e.g. 5) "))

        print(f'Loading quiz data, please wait...     allowed answers are {valid_responses}')
        for i in range(u_rounds):
            quiz_pool.append(generate_doppelname_w_freq())

        ii = 1
        # start quiz
        for q in quiz_pool:
            print(f"\n{ii}/{i+1}: Is the name '{q['name']}' (R)eal or (F)ake? ")

            while (u_answer := input("Answer? ")) not in valid_responses:
                print(f"Please answer one of {', '.join(valid_responses)}")

            if u_answer in ['r', 'R', 'real', 'Real']: u_answer = 'r'
            elif u_answer in ['f', 'F', 'fake', 'Fake']: u_answer = 'f'

            # scoring
            if u_answer == 'r' and q['realname'] is True:
                score += 1
                print(Fore.GREEN, "\U0001f44d Correct, this name is an authentic Doppelname!", Fore.RESET)
            elif u_answer == 'f' and q['realname'] is False:
                score += 1
                print(Fore.GREEN, "\U0001f44d Correct, this name is a fake Doppelname!", Fore.RESET)
            elif u_answer == 'f' and q['realname'] is True:
                print(Fore.RED,"❌ Nope, it's actually an authentic one...", Fore.RESET)
            elif u_answer == 'r' and q['realname'] is False:
                print(Fore.RED,"❌ Nope, it's actually a fake one...", Fore.RESET)

            ii += 1

        print(f"\nEND SCORE: {score} out of {u_rounds} ({round(score/u_rounds*100)}%)")


con.close()
