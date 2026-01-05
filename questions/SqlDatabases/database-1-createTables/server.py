import sqlite3
import random
import string
import pandas as pd
import numpy as np

fields = {str: "TEXT", int: "INTEGER",
          np.int64: "INTEGER", np.float64: "REAL"}


def fill_db(conn, table_name):
    conn.cursor().execute("DROP TABLE IF EXISTS {};"
                          .format(table_name))
    num_cols = random.randint(1, 4)
    df = pd.read_csv('../../../clientFilesCourse/faker.csv')
    cols = ['id'] + random.sample(list(df.keys()), num_cols)
    types = ['INTEGER PRIMARY KEY'] + \
        [fields[type(df[col][0])] for col in cols[1:]]

    col_string = []
    for col, col_type in zip(cols, types):
        col_string.append(col + ' ' + col_type)

    create_table = 'CREATE TABLE {} ({})'.format(
        table_name, ', '.join(col_string))
    conn.cursor().execute(create_table)

    return cols, types, create_table


def generate(data):
    conn_solution = sqlite3.connect("database.db")
    table_name = ''.join(random.choice(string.ascii_lowercase)
                         for i in range(5))
    cols, types, sol = fill_db(conn_solution, table_name)

    display_types = types.copy()
    for index in range(len(display_types)):
        if display_types[index] == 'INTEGER PRIMARY KEY':
            display_types[index] = 'INTEGER'

    data['params']['table_name'] = table_name
    data['params']['display_types'] = display_types
    data['params']['columns'] = cols
    data['params']['types'] = types
    data['params']['solution'] = sol
    conn_solution.close()
    return data


def parse(data):
    try:
        table_name = data['params']['table_name']
        conn_student = sqlite3.connect("s_database.db")
        conn_student.cursor().execute(
            'DROP TABLE IF EXISTS {}'.format(table_name))
        conn_student.cursor().execute(
            data['submitted_answers']['student_query'])
    except Exception as e:
        data['format_errors']['student_query'] = 'Syntax Error: {}'.format(
            str(e))


def grade(data):
    table_name = data['params']['table_name']
    conn_student = sqlite3.connect("s_database.db")
    conn_student.cursor().execute(
        'DROP TABLE IF EXISTS {}'.format(table_name))
    conn_student.cursor().execute(
        data['submitted_answers']['student_query'])

    student_structure = conn_student.cursor().execute(
        'PRAGMA TABLE_INFO({})'.format(table_name)).fetchall()

    conn_solution = sqlite3.connect("database.db")

    solution_structure = conn_solution.cursor().execute(
        'PRAGMA TABLE_INFO({})'.format(table_name)).fetchall()

    student_simp = simplify(student_structure)
    solution_simp = simplify(solution_structure)

    primary_key_flag = False
    if len(student_simp) == len(solution_simp):
        for index in range(len(student_simp)):
            if index == 0:
                if student_simp[index][1] == "INTEGER":
                    primary_key_flag = True
            else:
                if student_simp[index] != solution_simp[index]:
                    primary_key_flag = False

    data["feedback"]["student_query"] = student_simp

    data['score'] = int(set(student_simp) == set(solution_simp))
    if data['score'] == 1:
        data['feedback']['message'] = "Correct!"
    else:
        if primary_key_flag:
            data['feedback']['message'] = "The statement entered did not create \
            the expected table because id was not specified as the primary key."
        else:
            data['feedback']['message'] = "The statement entered did not create \
            the expected table."

    conn_solution.close()
    conn_student.close()
    return data


def simplify(structure):
    simplified = []
    for col in structure:
        temp = (
            col[1],
            col[2] + (' PRIMARY KEY' if col[5] else '')
        )
        simplified.append(temp)
    return simplified
