import sqlite3
import random as rand
import json
import pandas as pd

# load in file with table groups
with open("../../../clientFilesCourse/table.json", "r") as read_file:
    tables = json.load(read_file)

# open database & choose table
conn_solution = sqlite3.connect("database.db")
group_number = rand.randint(0, len(tables) - 1)
table_number = rand.randint(0, len(tables[group_number]) - 1)
table_name = tables[group_number][table_number]["table_name"]
faker = pd.read_csv('../../../clientFilesCourse/faker.csv')
columns = tables[group_number][table_number]["columns"]
faker_columns = list(faker.head(0))


# function to replace placeholders with faker data
def fill_with_faker(table_number, rows, conditions):
    for index in range(len(tables[group_number][table_number]["columns"])):

        c = tables[group_number][table_number]["columns"][index]

        if c in faker_columns:
            values, used, cond_vals = rand.sample(list(faker[c]), 5), [], []
            for row_number in range(len(rows)):
                if isinstance(rows[row_number][index], str) and rows[row_number][index].find("Fake") > -1:
                    rows[row_number][index] = rand.choice(values)
                    if rows[row_number][index] in used:
                        cond_vals.append(rows[row_number][index])
                    used.append(rows[row_number][index])
            for condition_number in range(len(conditions)):
                if "Fake <" + c + ">" in conditions[condition_number]:
                    try:
                        conditions[condition_number] = conditions[condition_number]\
                            .replace("Fake <" + c + ">", str(rand.choice(cond_vals)))
                    except:
                        conditions[condition_number] = conditions[condition_number]\
                            .replace("Fake <" + c + ">", str(rand.choice(used)))

        if "year" in c:
            values, used, cond_vals = rand.sample(list(faker["year"]), 5), [], []
            for row_number in range(len(rows)):
                if isinstance(rows[row_number][index], str) and rows[row_number][index].find("Fake") > -1:
                    rows[row_number][index] = rand.choice(values)
                    if rows[row_number][index] in used:
                        cond_vals.append(rows[row_number][index])
                    used.append(rows[row_number][index])
            for condition_number in range(len(conditions)):
                if "Fake <" + c + ">" in conditions[condition_number]:
                    try:
                        conditions[condition_number] = conditions[condition_number]\
                            .replace("Fake <" + c + ">", str(rand.choice(cond_vals)))
                    except:
                        conditions[condition_number] = conditions[condition_number]\
                            .replace("Fake <" + c + ">", str(rand.choice(used)))

    return rows, conditions


rows, conditions = fill_with_faker(table_number, tables[group_number][table_number]["rows"],
                                   tables[group_number][table_number]["conditions"])


# function to get rid of foreign keys
def rid_fk():
    rm = []
    for index in range(len(columns)):
        if columns[index].find("id") > -1 and columns[index] != "id":
            rm.append(columns[index])
            for row in rows:
                row.remove(row[index])
    create = tables[group_number][table_number]["create"]
    for column in rm:
        columns.remove(column)
        start_index = int(create.find(column))
        end_index = int(start_index + len(column) + len(" INTEGER, "))
        substring = create[start_index:end_index]
        create = create.replace(substring, '')

    flag = create.find("FOREIGN")
    if flag > -1:
        flag -= 2
        create = create[0:flag]
        create = create + ")"

    return columns, rows, create


# function to insert rows into SQL table
def fill_db_fk(conn, table_name, table_number, rows, create):
    conn.cursor().execute("DROP TABLE IF EXISTS {};"
                          .format(table_name))
    conn.cursor().execute(create)
    num_cols = len(rows[0])
    for outer_index in range(len(rows)):
        row = "("
        for inner_index in range(num_cols):
            col_val = rows[outer_index][inner_index]
            if isinstance(col_val, str):
                col_val = "\"" + col_val + "\""
            else:
                col_val = str(col_val)
            if inner_index == num_cols - 1:
                row += col_val + ")"
            else:
                row += col_val + ", "
        insert = "INSERT INTO " + table_name + " VALUES " + row
        conn.cursor().execute(insert)
    conn.commit()


# get rid of foreign keys from tables file
columns, rows, create = rid_fk()


# fill databse with chosen table
fill_db_fk(conn_solution, table_name, table_number, rows, create)
cursor = conn_solution.cursor()


# function to build default query
def build_default_query():
    return "select * FROM {}".format(table_name)


# function to get table data in a dictionary
def get_table_data(query):
    return [{"data": list(entry)} for entry in conn_solution.cursor().execute(
                query).fetchall()]


# function that builds a query given necessary information
def build_query(columns, condition):
    return "SELECT " + columns + " FROM {t} {c}".format(t=table_name,
                                                        c=condition)


# function to randomly choose a condition
def choose_condition(conditions):
    cond_chooser = rand.randint(0, len(conditions) - 1)
    condition = " " + str(conditions[cond_chooser])
    return condition


# function to randomly choose columns to select
def choose_columns(columns):
    columns_str = ""
    columns_q, keys = [], []
    cols = columns.copy()
    for col in cols:
        if col.find("id") > -1:
            keys.append(col)
    for key in keys:
        cols.remove(key)
    num_selected = rand.randint(2, len(cols))
    for index in range(num_selected):
        col = rand.choice(cols)
        columns_q.append(col)
        cols.remove(col)
    id_or_not = rand.randint(0, 1)
    if id_or_not == 0:
        columns_q.insert(0, "id")
    columns_str = str(columns_q).replace("[", "")
    columns_str = columns_str.replace("]", "")
    columns_str = columns_str.replace("\'", "")
    return columns_str, columns_q


def generate(data):

    # build question variant
    query = build_default_query()
    condition = rand.choice(conditions)
    columns_str, data["params"]["columns_q"] = choose_columns(columns)
    solution_query = build_query(columns_str, condition)
    table_data = get_table_data(query)
    table_data_q = get_table_data(solution_query)
    # cursor = conn_solution.cursor().execute(solution_query)

    # add necessary information to datadict
    data["params"]["table_data"] = table_data
    data["params"]["table_data_q"] = table_data_q
    data["params"]["table_name"] = table_name
    data["params"]["solution"] = solution_query
    data["params"]["columns"] = columns

    conn_solution.close()
    return data


# function to catch invalid & blank inputs
def parse(data):

    student_columns = data["submitted_answers"]["columns"]
    student_condition = data["submitted_answers"]["condition"]
    table_name = data["params"]["table_name"]

    try:
        student_answer = "SELECT " + student_columns + " FROM {} WHERE ".format(table_name) \
                                                                                + student_condition
        cursor.execute(student_answer)
    except sqlite3.Error as e:
        data["format_errors"]["student_feedback"] = "The SQL query entered is invalid: \"" + e.args[0] + "\""
    except Exception as e:
        data["format_errors"]["regex"] = str(e)
        data["format_errors"]["student_feedback"] = "The SQL query entered is invalid."

    return data


# function to change column data in a table to disregard order
def column_order(data_list):
    for element in data_list:
        for index in range(len(element)):
            if not isinstance(element[index], str):
                element[index] = str(element[index])
        element = element.sort()
        element = str(element)
    data_list.sort()
    return data_list


# function that readies table data for comparioson
def grade_helper(query):
    results = cursor.execute(query)
    columns = [description[0] for description in results.description]
    results = results.fetchall()
    return columns, column_order([list(entry) for entry in results])


# function to determine partial credit for rows retrieved
def partial_rows(pa, spa):
    results = cursor.execute(pa).fetchall()
    results2 = cursor.execute(spa).fetchall()
    return ([list(r)[0] for r in results] == [list(r)[0] for r in results2])


# function to determine partial credit for columns selected
def partial_cols(sol_c, stu_c):
    sol_c.sort()
    stu_c.sort()
    return (stu_c == sol_c)


# function to build queries needed to test row retrieved partial credit
def build_partial_query(condition):
    return "SELECT * FROM {} ".format(table_name) + condition


# function to generate binary string as index for feedback
def feedback_list_index(rows, cols):
    r, c = int(rows is True), int(cols is True)
    return ((r << 1) | c)


# function to determine score for incorrect answers
def get_score(index):
    return (int(100 * (bin(index).count("1") / 2)) / 100.0)


def grade(data):
    # indicate arrival in grade function, get appropriate data, & build partial answers
    data["correct_answers"]["flag"] = 1
    solution, table_name = data["params"]["solution"], data["params"]["table_name"]
    student_columns = data["submitted_answers"]["columns"]
    student_condition = data["submitted_answers"]["condition"]
    student_answer = "SELECT " + student_columns + \
        " FROM {} WHERE ".format(table_name) + student_condition
    student_partial_answer = build_partial_query("WHERE " + student_condition)
    partial_answer = build_partial_query(solution[solution.find("WHERE"):])

    # grading of student answer
    solution_columns, data1 = grade_helper(solution)
    student_columns, data2 = grade_helper(student_answer)
    student_columns_for_partial = student_columns.copy()
    data["feedback"]["columns_s"] = student_columns
    if(data1 == data2):
        data["score"], data["feedback"]["message"] = 1, "Correct!"
    else:
        row_matching = partial_rows(partial_answer, student_partial_answer)
        column_matching = partial_cols(solution_columns, student_columns_for_partial)
        index = feedback_list_index(row_matching, column_matching)
        data["score"], data["feedback"]["message"] = get_score(index), feedback_list[index]

    # add necessary information to data dictionary
    data["feedback"]["student_results"] = [
        {"data": list(entry)} for entry in cursor.execute(student_answer)]
    data["feedback"]["results"] = "Your Results"

    return data


# list with all potential feedback messages for incorrect answers
feedback_list = ["Both the columns selected and rows retrieved \
                        were incorrect.", "The columns selected were correct, \
                        but the rows retrieved were incorrect.",  "The rows \
                        retrieved were correct, \
                        but the columns selected were incorrect."]
