# Doppelnamen-Quiz

A Python script to generate random _Doppelnamen_ (double surname) and check, if they really exist in Austria.

Based on a SQLite3 database with a `prefix` and a `suffix` table of typical Austrian surnames, random _Doppelnamen_ 
can be generated. To verify their authenticity, they are checked against three sources:
- crawling `Herold.at`, Austria's most important phone book
- crawling `TelefonABC.at`, another Austraian phone book
- `Google API` (with country restriction `cr=countryAT`)
- initially, the Adler list of surnames was included as well, but later removed: https://tng.adler-wien.eu/surnames-all.php?tree=adler_person

The script (`main.py`) can be used in three modes: 

### Mode 1: List generation
Generate x random _Doppelnamen_ and return their actual frequency

```pycon
Please select mode:  1
How many names should be generated (e.g. 5) 2

{   'freq_abc': 1,
    'freq_google': 18900,
    'freq_herold': 2,
    'name': 'Altbauer',
    'realname': True}
{   'name': 'Lichtenmann', 
    'realname': False}
```

### Mode 2: User input
Check user input for authenticity and return actual frequency for this one name. 
Warning: All user input will be written to the database and later used in Mode 3!

```pycon
Please select mode:  2
Which Doppelname do you want to check?  Doppelbauer

{   'freq_abc': 85,
    'freq_adler': None,
    'freq_google': 39600,
    'freq_herold': 96,
    'name': 'Doppelbauer',
    'realname': True}
```

### Mode 3: Interactive quiz

```pycon
Please select mode:  3
How many quiz rounds do you want to play? (e.g. 5) 3
Loading quiz data, please wait...     allowed answers are ['r', 'R', 'real', 'Real', 'f', 'F', 'fake', 'Fake']

1/3: Is the name 'Neutorfer' (R)eal or (F)ake? 
Answer? r
 ❌ Nope, it's actually a fake one... 

2/3: Is the name 'Lehstetter' (R)eal or (F)ake? 
Answer? f
 👍 Correct, this name is a fake Doppelname! 

...
```

## Installation
Use [pip](https://pip.pypa.io/en/stable/) to install using `requirements.txt`.

```bash
pip install -r requirements.txt
```
Then, add your personal Google Developer API key to the `.env` file