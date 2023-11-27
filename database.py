import mysql.connector as mysql
from config import *
import csv
def connection(database=None):
    args = {
        'host': HOST,
        'port': PORT,
        'user': USER,
        'password': PASSWORD,
        'use_pure': True
    }
    if database:
        args['database'] = database
    return mysql.connect(**args)

try:
    print(f"Connecting to MySQL server on {HOST}:{PORT}...")
    conn = connection()
except mysql.errors.ProgrammingError:
    print("MySQL User or password incorrect in config.ini")
    exit()
except mysql.errors.InterfaceError:
    print("Can't connect to the MySQL Server.")
    print("Make sure that the server is running")
    exit()

def createDB():
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE {DATABASE}")
    cursor.close()

def source(filename, *args, output=True, lastRowId=False):
    cursor = conn.cursor(buffered=output)
    with open('sql/' + filename) as f:
        statements = f.read()
        statements = statements.replace('\n', ' ')
        statements = statements.replace(';', '\n')
        for statement in statements.strip().splitlines():
            if args:
                cursor.execute(statement, args) if statement else None
                break
            cursor.execute(statement) if statement else None

    if output:
        result = cursor.fetchall()
    if lastRowId:
        result = cursor.lastrowid
    conn.commit()
    cursor.close()
    if output or lastRowId:
        return result

def import_from_csv(name, filename):
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        if name == 'cust':
            for row in reader:
                row[4] = int(row[4])
                source("newpassenger.sql", *row, output=False)
        elif name == 'res':
            for row in reader:
                row[0], row[1], row[5] = map(int, (row[0], row[1], row[5]))
                source("new_reservation.sql", *row, output=False)
        elif name == 'room':
            for row in reader:
                row[0], row[3], row[4] = map(int, (row[0], row[3], row[4]))
                source("newbus.sql", *row, output=False)
        elif name == 'room_type':
            for row in reader:
                row[2] = int(row[2])
                source("newbustype.sql", *row, output=False)
        elif name == 'tnx':
            for row in reader:
                row[4], row[6], row[7] = map(int, (row[4], row[6], row[7]))
                for i in (1,2):
                    if row[i] == 'NULL':
                        row[i] = None
                    else:
                        row[i] = int(row[i])
                source("new_transaction.sql", *row, output=False)
        elif name == 'emp':
            for row in reader:
                row[0], row[4] = int(row[0]), int(row[4])
                source("new_employee.sql", *row, output=False)
        elif name == 'job':
            for row in reader:
                row[1] = int(row[1])
                source("new_job.sql", *row, output=False)

def new(newname, newfile):
    with open(newfile, 'w') as file:
        file.write(f'"""\n')
        file.write(f'{newname}\n')
        file.write(f'Write your code here\n')
        file.write(f'"""\n\n')

        for line_number in range(1, 31):
            file.write(f'# Line {line_number}\n')

def export_to_csv(name, filename):
    if name == 'Customer':
        fields = ['cust_id', 'cust_fname', 'cust_lname', 'cust_address', 'cust_ph_no', 'status']
        rows = source("allpassengers.sql")
    elif name == 'Employee':
        fields = ['emp_id', 'job_id', 'emp_fname', 'emp_lname', 'emp_address', 'emp_ph_no']
        rows = source("all_employees.sql")
    elif name == 'Job':
        fields = ['job_id', 'job_title', 'salary']
        rows = source("all_employees.sql")
    elif name == 'Reservation':
        fields = ['res_id', 'cust_id', 'room_id', 'transaction_id', 'stop1_expected', 'stop1_real', 'stop2_expected', 'stop2_real', 'fine']
        rows = source("all_reservations.sql")
    elif name == 'Room_Type':
        fields = ['type_id', 'name', 'capacity']
        rows = source("allbustypes.sql")
    elif name == 'Room':
        fields = ['room_id', 'type_id', 'description', 'price', 'occupancy_status']
        rows = source("allbuses.sql")
    elif name == 'Transaction':
        fields = ['transaction_id', 'emp_id', 'res_id', 'dated', 'amount', 'payment_mode', 'type', 'status']
        rows = source("all_transactions.sql")
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)


def clear():
    global conn
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {DATABASE}")
    cur.close()
    createDB()
    conn = connection(DATABASE)
    source('tables_schema.sql', output=False)


print(f"Connecting to {DATABASE} database...")
cur = conn.cursor(buffered=True)
newDB = False
cur.execute("SHOW DATABASES")
if (DATABASE,) not in cur.fetchall():
    print(f"No database named {DATABASE} found. Creating Database...")
    createDB()
    newDB = True
cur.close()
conn.close()
conn = connection(DATABASE)
if newDB:
    print("Creating required tables in the database...")
    source('tables_schema.sql', output=False)
    
if __name__ == '__main__':
    print("Running this script explicitly will delete the database with name as in config.ini")
    x = input("Do you want to delete the database? [Y/n] ").upper()
    if x == 'Y' or x == 'YES':
        cur = conn.cursor()
        cur.execute(f"DROP DATABASE IF EXISTS {DATABASE}")
        cur.close()
        print("database deleted")
    print(conn)
    conn.close()