import sqlite3 as sl
import pandas as pd

# Create/Connect database
conn = sl.connect('grad.db')
curs = conn.cursor()

# # Create our table
# # Manually specify table name, column names, and columns types
# curs.execute('DROP TABLE IF EXISTS grad')
# curs.execute('CREATE TABLE IF NOT EXISTS '
#              'grad (`SerialNo` number, `GRE` number, `TOEFL` number, `URating` number, `SOP` number, `LOR` number, `CGPA` number, `Research` number, `COA` number)')
# # grad (`SerialNo.` number, `GRE` number, `TOEFL` number, `URating` number, `SOP` number, `LOR` number, `CGPA` number, `Research` number, `Choice` number)
# conn.commit()  # don't forget to commit changes before continuing
#
values = []
with open('Admission_Predict_Ver1.1.csv') as fin:
    for line in fin:
        # print(line)
        line = line.strip()
        if line:
            line = line.replace('\"', '')  # get rid of wrapping double quotes
            lineList = line.split(',')     # split on comma (CSV)
            # only accept rows w/ a last column that has a valid temp
            if lineList and lineList[0].strip().isnumeric():
                # print(lineList)
                #                     -4          -3         -2         -1
                # ['USC00454486', 'LANDSBURG', ' WA US', '2021-12-26', '23']
                #
                # [1, 337, 118, 4, 4.5, 4.5, 9.65, 1, 0.92]
                #
                valTuple = (lineList[0], lineList[1],  # re-combine city, state
                            lineList[2], lineList[3],
                            lineList[4], lineList[5],
                            lineList[6], lineList[7],
                            lineList[8])
                values.append(valTuple)
for val in values:
    print(val)

for valTuple in values:
    stmt = 'INSERT OR IGNORE INTO grad VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
    curs.execute(stmt, valTuple)

conn.commit()

# The rest is from the DB lecture and HW


curs.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_names = [table[0] for table in curs.fetchall()]
print(table_names)



print('\nFirst 3 db results:')
results = curs.execute('SELECT * FROM grad').fetchmany(3)
for result in results:
    print(result)

result = curs.execute('SELECT COUNT(*) FROM grad').fetchone()
# Note indexing into the always returned tuple w/ [0]
# even if it's a tuple of one
print('\nNumber of valid db rows:', result[0])

result = curs.execute('SELECT MAX(`COA`) FROM grad').fetchone()
print('Max Observed COA', result[0])

curs.close()
conn.close()