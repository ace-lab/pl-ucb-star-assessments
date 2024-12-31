import sqlite3
import random as rand
import json
import pandas as pd
import csv

# load in file with table groups
with open("../../../clientFilesCourse/table.json", "r") as read_file:
    tables = json.load(read_file)

# randomly choose table group from list of table groups
group_number = rand.randint(0, 1)
conn_solution = sqlite3.connect("database.db")
cursor = conn_solution.cursor()
table_1_number, table_2_number = 0, rand.randint(1, len(tables[group_number])-1)
table_1_name = tables[group_number][table_1_number]["table_name"]
table_2_name = tables[group_number][table_2_number]["table_name"]
order = rand.choice([0, 1, 1, 1])
faker = pd.read_csv('../../../clientFilesCourse/faker.csv')
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


# retrieve rows and conditions with faker values
rows_1, conditions_1 = fill_with_faker(0,
                                       tables[group_number][table_1_number]["rows"],
                                       tables[group_number][table_1_number]["conditions"])
rows_2, conditions_2 = fill_with_faker(table_2_number, tables[group_number][table_2_number]["rows"],
                                       tables[group_number][table_2_number]["conditions"])


# function to insert rows into SQL table
def fill_db_fk(conn, table_name, table_number, rows):
    conn.cursor().execute("DROP TABLE IF EXISTS {};"
                          .format(table_name))
    conn.cursor().execute(tables[group_number][table_number]["create"])
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


# function to get table data in a dictionary
def get_table_data(query):
    return [{"data": list(entry)} for entry in conn_solution.cursor().execute(
            query).fetchall()]


# function that returns a query that selects all columns from a table
def default_query(table_name):
    return "select * FROM {}".format(table_name)


# function to find primary key of parent table
def find_primary_key(table_number):
    create_string = tables[group_number][table_number]["create"]
    create_string = create_string.replace("(", " ")
    create_string = create_string.replace(")", " ")
    create_string = create_string.replace(",", "")
    create_string = create_string.split()
    for index in range(len(create_string)):
        if (create_string[index] == 'PRIMARY') and (create_string[index + 1] == 'KEY'):
            return create_string[index - 2]


# function to find foreign key of child table
def find_foreign_key():
    create_string = tables[group_number][table_2_number]["create"]
    create_string = create_string.replace("(", " ")
    create_string = create_string.replace(")", " ")
    create_string = create_string.replace(",", "")
    create_string = create_string.split()
    for index in range(len(create_string)):
        if (create_string[index] == 'FOREIGN') and (create_string[index + 1] == 'KEY'):
            return create_string[index + 2]


# function to randomly choose columns to select
def choose_columns(columns, pk, fk, cpk):
    columns_str = ""
    columns_q = []
    cols = columns.copy()
    cols.remove(pk)
    cols.remove(fk)
    if cpk in cols:
        cols.remove(cpk)
    if "id" in cols:
        cols.remove("id")
    num_selected = rand.randint(2, len(cols))
    for index in range(num_selected):
        col = rand.choice(cols)
        columns_q.append(col)
        cols.remove(col)
    columns_str = str(columns_q).replace("[", "")
    columns_str = columns_str.replace("]", "")
    columns_str = columns_str.replace("\'", "")
    return columns_str, columns_q


# function to randomly choose a condition
def choose_condition(conditions):
    cond_chooser = rand.randint(0, len(conditions) - 1)
    condition = " " + str(conditions[cond_chooser])
    return condition


# function that builds a query given necessary information
def build_query(columns, primary_key, foreign_key, condition):
    return "SELECT " + columns + " FROM {t1} JOIN {t2} \
            ON {t1}.{pk} = {t2}.{fk}{c}".format(t1=table_1_name,
                                                t2=table_2_name,
                                                pk=primary_key,
                                                fk=foreign_key,
                                                c=condition)


def generate(data):

    # fill databses with the two chosen table
    fill_db_fk(conn_solution, table_1_name, table_1_number, rows_1)
    fill_db_fk(conn_solution, table_2_name, table_2_number, rows_2)

    # build a solution query & default queries
    query1 = default_query(table_1_name)
    query2 = default_query(table_2_name)
    data["params"]["columns_1"] = tables[group_number][table_1_number]["columns"]
    data["params"]["columns_2"] = tables[group_number][table_2_number]["columns"]
    columns = data["params"]["columns_1"] + data["params"]["columns_2"]
    primary_key, foreign_key = find_primary_key(table_1_number), find_foreign_key()
    child_table_primary_key = find_primary_key(table_2_number)
    columns_str, data["params"]["columns_q"] = \
        choose_columns(columns, primary_key, foreign_key, child_table_primary_key)
    conditions = conditions_1 + conditions_2
    condition = choose_condition(conditions)
    solution_query = build_query(columns_str, primary_key, foreign_key, condition)

    # fill datadict with remaining appropriate values
    data["params"]["table_1_data"] = get_table_data(query1)
    data["params"]["table_2_data"] = get_table_data(query2)
    data["params"]["table_data_q"] = get_table_data(solution_query)
    data["params"]["table_1_name"] = table_1_name
    data["params"]["table_2_name"] = table_2_name
    data["params"]["solution"] = solution_query
    data["params"]["primary_key"] = primary_key
    data["params"]["foreign_key"] = foreign_key

    conn_solution.close()
    return data


# function to catch invalid & blank inputs
def parse(data):

    try:
        student_answer = "SELECT " + data["submitted_answers"]["columns"] + " FROM {t1} \
                JOIN {t2} ON ".format(t1=data["params"]["table_1_name"], t2=data["params"]["table_2_name"])\
                + data["submitted_answers"]["on"] + " WHERE " + data["submitted_answers"]["condition"]
        cursor.execute(student_answer)
    except sqlite3.Error as e:
        data["format_errors"]["student_feedback"] = "The SQL query entered is invalid: \"" + e.args[0] + "\""
    except Exception as e:
        data["format_errors"]["query"] = str(e)
        data["format_errors"]["student_feedback"] = "The SQL query entered is invalid."

    return data


# function to build queries needed to test row retrieved partial credit
def build_partial_query(primary_key, foreign_key, condition):
    return "SELECT * FROM {t1} \
            JOIN {t2} ON {t1}.{pk} = {t2}.{fk}".format(t1=table_1_name,
                                                             t2=table_2_name,
                                                             pk=primary_key,
                                                             fk=foreign_key) + condition


# function that readies table data for comparioson
def grade_helper(query, flag):
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


# function to determine partial credit for join statement
def partial_join(join_statement, primary_key, foreign_key):
    join_statement = join_statement.replace(" ", "")
    return (join_statement == "{t1}.{pk}={t2}.{fk}".format(pk=primary_key,
                                                           t2=table_2_name,
                                                           t1=table_1_name, fk=foreign_key) or
            (join_statement == "{t2}.{fk}={t1}.{pk}".format(pk=primary_key,
                                                            t2=table_2_name,
                                                            t1=table_1_name,
                                                            fk=foreign_key)) or
            (join_statement == "{fk}={t1}.{pk}".format(pk=primary_key,
                                                       fk=foreign_key,
                                                       t1=table_1_name)) or
            (join_statement == "{t1}.{pk}={fk}".format(pk=primary_key,
                                                       fk=foreign_key,
                                                       t1=table_1_name)))


# function to generate binary string as index for feedback
def feedback_list_index(rows, cols, join):
    r, c, j = int(rows is True), int(cols is True), int(join is True)
    return ((r << 2) | (c << 1) | j)


# function to determine score for incorrect answers
def get_score(index):
    return (int(100 * (bin(index).count("1") / 3)) / 100.0)


def grade(data):
    # indicate arrival in grade funciton & build student and partial credit queries
    data["correct_answers"]["flag"] = 1
    solution = data["params"]["solution"]
    primary_key, foreign_key = data["params"]["primary_key"], data["params"]["foreign_key"]
    student_answer = "SELECT " + data["submitted_answers"]["columns"] + \
        " FROM {t1} JOIN {t2} ON ".format(t1=data["params"]["table_1_name"],
                                                t2=data["params"]["table_2_name"]) \
        + data["submitted_answers"]["on"] \
        + " WHERE " \
        + data["submitted_answers"]["condition"]
    student_partial_answer = build_partial_query(primary_key,
                                                 foreign_key,
                                                 " WHERE " + data["submitted_answers"]["condition"])
    partial_answer = build_partial_query(primary_key, foreign_key, " " + solution[solution.find("WHERE"):])

    # check student solution and assign scores appropriately
    solution_columns, data1 = grade_helper(solution, 0)
    student_columns, data2 = grade_helper(student_answer, 1)
    student_columns_for_partial = student_columns.copy()
    if(data1 == data2):
        data["score"], data["feedback"]["message"] = 1, "Correct!"
    else:
        row_matching = partial_rows(partial_answer, student_partial_answer)
        column_matching = partial_cols(solution_columns, student_columns_for_partial)
        join_matching = partial_join(data["submitted_answers"]["on"], primary_key, foreign_key)
        index = feedback_list_index(row_matching, column_matching, join_matching)
        data["score"], data["feedback"]["message"] = get_score(index), feedback_list[index]

    # add appropriate data for feedback
    data["feedback"]["student_results"] = [
        {"data": list(entry)} for entry in cursor.execute(student_answer)]
    data["feedback"]["columns_s"] = student_columns

    return data


# list with all potential feedback messages for incorrect answers
feedback_list = ["All three inputs are incorrect.",
                 "The join statement was correct, but the rows retrieved and columns selected \
                 did not match the expected result.", "The columns selected were correct, \
                 but the join statement was incorrect and the rows that would have been \
                 retrieved did not match the expected result.", "The columns selected and \
                 the join statement were correct, but the rows retrieved did not match the \
                 expected result.", "The columns selected and the join statement were incorrect,\
                 but the rows retrieved would have been correct.", "The join statement and the \
                 rows retrieved were correct, but the columns selected did not match the \
                 expected result.", "The columns selected and rows retrieved would have been \
                 correct, but the join statement was incorrect."]
