import re
import camelot
import sqlite3
from datetime import datetime
from datetime import date, timedelta

# download pdf with wget

# decrypt pdf with qpdf
# qpdf --password=5290 --decrypt test.pdf camtest.pdf

# convert pdf to text, can consider decreasing 5 if issues
# pdftotext -opw 5290 -fixed 5 test.pdf

# open pdftotext file
lines = []
with open('advance_schedule.txt') as f:
    lines = f.readlines()

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

# get the first date in advance schedule, table 0, row 2, value 0
#raw_date = tables[0][2][0]
#raw_date = raw_date.split('/')
# create a date from raw_date passing year, month, day
#first_date = date(int(raw_date[2]), int(raw_date[0]), int(raw_date[1]))

# get the first assignment date
raw_date = lines[2].split(maxsplit=1)[0].strip()
split_date = raw_date.split('/')
first_date = date(int(split_date[2]), int(split_date[0]), int(split_date[1]))

tables = []
rows = []
keep_row = False
for line in lines:
    if not line.strip(): continue
    header = line.split(maxsplit=1)[0].strip()
    if header == '*': continue
    if header == raw_date: keep_row = True
    if header == 'W':
        tables.append(rows)
        rows = []
        keep_row = False
    if keep_row: rows.append(line.strip('\n'))

# parse the text version of the assignments 
for table in tables:
    # find the end index after match
    # end_indices = [match.end() for match in re.finditer("\S\S*", table[0])]
    end_indices = []
    matches = re.finditer("\S\S*", table[0])
    # skip first match and add the start of second instead
    next(matches)
    second_match = next(matches)
    end_indices.append(second_match.start() - 1)
    end_indices.append(second_match.end())
    for match in matches:
        end_indices.append(match.end())
    # no need for divider at very end
    end_indices = end_indices[:-1]
    
    # add dividers to the table
    for k, row in enumerate(table):
        for i in end_indices:
            row = row[:i] + '|' + row[i+1:]
        # split along those dividers
        print(row)
        table[k] = [value.strip() for value in row.split('|')]

for table in tables:
    for row in table[1:]:
        anes = row[0].split('/')[::-1][0].strip()
        print(len(row), end=' ')
        print(anes, end=' ')
        print(row[1:])
        # set the date to the first date of the table
        cur_date = first_date
        # add the assignments for each anesthesiologist
        for assignment in row[1:]:
            assignment = assignment.strip()
            cursor.execute(f'''
                REPLACE INTO assignments (date, anesthesiologist, assignment)
                VALUES ('{cur_date}', '{anes}', '{assignment}');''');
            cur_date = cur_date + timedelta(days=1)
    # initialize the first date for the next table
    first_date = cur_date

connection.commit()
connection.close()
