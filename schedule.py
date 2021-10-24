import camelot
import sqlite3
from datetime import datetime

# download pdf with wget

# decrypt pdf with qpdf
# qpdf --password=5290 --decrypt test.pdf camtest.pdf

# convert pdf to text with pdftotext
# pdftotext camtest.pdf

# figure out how to get year and month
lines = []
with open('camtest.txt') as f:
    lines = f.readlines()

# month and year are on second line, convert month to number
year = lines[1].split()[1].strip()
month = datetime.strptime(lines[1].split()[0].strip(), "%B").month

# create or connect to database and create assignments table if not exist
connection = sqlite3.connect('schedule.db')
cursor = connection.cursor();
cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            assignment_id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            anesthesiologist TEXT NOT NULL,
            assignment TEXT NOT NULL,
            UNIQUE(date, anesthesiologist));''')


# get array from pdf, decrypt with qpdf
tables = camelot.read_pdf('camtest.pdf', flavor = 'stream')
table = tables[0]
df = table.df 
assignments = df.to_numpy()

# first and second rows are not assignments
for anesthesiologists in assignments[2:]:
    # first item in row is anesthesiologists name or blank
    anesthesiologist = anesthesiologists[0]
    if (anesthesiologist):
        for (day, assignment) in enumerate(anesthesiologists[1:], start = 1):
            # add assignments to database, add leading zeros for ISO date format
            # 0>2s = pad with 0, align var to > right, 2 width, var is s string, d decimal
            cursor.execute(f'''
                REPLACE INTO assignments (date, anesthesiologist, assignment)
                VALUES ('{year:0>4s}-{month:0>2d}-{day:0>2d}', '{anesthesiologist}', '{assignment}');''');

connection.commit()
connection.close()
