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
rows_1, conditions_1 = fill_with_faker(0, tables[group_number][table_1_number]["rows"],
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
    entries = []
    for entry in conn_solution.cursor().execute(query).fetchall():
        entry = list(entry)
        for index in range(len(entry)):
            if entry[index] is None:
                entry[index] = 'NULL'
        entries.append(tuple(entry))
    return [{"data": list(entry)} for entry in entries]


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


# function find key to compare tables on
def find_key(table_number):
    create_string = tables[group_number][table_2_number]["create"]
    create_string = create_string.replace("(", " ")
    create_string = create_string.replace(")", " ")
    create_string = create_string.replace(",", "")
    create_string = create_string.split()
    for index in range(len(create_string)):
        if (create_string[index] == 'PRIMARY') and (create_string[index + 1] == 'KEY'):
            return create_string[index + 2]


# function to randomly choose columns to select
def choose_columns(columns, fk, pk1, pk2, num_cols):
    columns_str = ""
    columns_q = []
    cols = columns.copy()
    while fk in cols:
        cols.remove(fk)
    cols.remove(pk1)
    cols.remove(pk2)
    num_selected = rand.randint(num_cols, len(cols))
    for index in range(num_selected):
        col = rand.choice(cols)
        columns_q.append(col)
        cols.remove(col)
    columns_str = str(columns_q).replace("[", "")
    columns_str = columns_str.replace("]", "")
    columns_str = columns_str.replace("\'", "")
    return columns_str, columns_q


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


# function to randomly choose a condition
def choose_condition(conditions):
    cond_chooser = rand.randint(0, len(conditions) - 1)
    condition = " " + str(conditions[cond_chooser])
    return condition


# function that builds a query given necessary information
def build_query(columns, key1, key2, condition):
    if order == 0:
        return "SELECT " + columns + " FROM {t2} LEFT JOIN {t1} \
                ON {t1}.{k1} = {t2}.{k2}{c}".format(t1=table_1_name,
                                                    t2=table_2_name, k1=key1, k2=key2, c=condition)
    else:
        return "SELECT " + columns + " FROM {t1} LEFT JOIN {t2} \
                ON {t1}.{k1} = {t2}.{k2}{c}".format(t1=table_1_name,
                                                    t2=table_2_name, k1=key1, k2=key2, c=condition)


def generate(data):

    # fill databses with the two chosen table
    fill_db_fk(conn_solution, table_1_name, table_1_number, rows_1)
    fill_db_fk(conn_solution, table_2_name, table_2_number, rows_2)

    # build a solution query & default queries
    query1 = default_query(table_1_name)
    query2 = default_query(table_2_name)
    data["params"]["columns_1"] = tables[group_number][table_1_number]["columns"]
    data["params"]["columns_2"] = tables[group_number][table_2_number]["columns"]
    num_columns = min(len(data["params"]["columns_1"]), len(data["params"]["columns_2"]))
    columns = data["params"]["columns_1"] + data["params"]["columns_2"]
    pk_1, pk_2 = find_primary_key(table_1_number), find_primary_key(table_2_number)
    fk = find_foreign_key()
    columns_str, data["params"]["columns_q"] = \
        choose_columns(columns, fk, pk_1, pk_2, num_columns)
    conditions = conditions_1 + conditions_2
    condition = choose_condition(conditions)
    solution_query = build_query(columns_str, pk_1, fk, condition)

    # fill datadict with remaining appropriate values
    data["params"]["table_1_data"] = get_table_data(query1)
    data["params"]["table_2_data"] = get_table_data(query2)
    data["params"]["table_data_q"] = get_table_data(solution_query)
    data["params"]["table_1_name"] = table_1_name
    data["params"]["table_2_name"] = table_2_name
    data["params"]["solution"] = solution_query
    data["params"]["foreign_key"] = fk
    data["params"]["primary_key"] = pk_1

    conn_solution.close()
    return data


# function to catch invalid & blank inputs
def parse(data):

    try:
        student_answer = "SELECT " + data["submitted_answers"]["columns"] + " FROM " + \
                data["submitted_answers"]["table_1"] + " LEFT JOIN " + data["submitted_answers"]["table_2"] \
                + " ON " + data["submitted_answers"]["on"] + " WHERE " + data["submitted_answers"]["condition"]
        cursor.execute(student_answer)
    except sqlite3.Error as e:
        data["format_errors"]["student_feedback"] = "The SQL query entered is invalid: \"" + e.args[0] + "\""
    except Exception as e:
        data["format_errors"]["query"] = str(e)
        data["format_errors"]["student_feedback"] = "The SQL query entered is invalid."

    return data


# function that readies table data for comparioson
def grade_helper(query, flag):
    results = cursor.execute(query)
    columns = [description[0] for description in results.description]
    results = results.fetchall()
    if flag == 1:
        return column_order([list(entry) for entry in results])
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
def partial_join(p_k, f_k, statement):
    statement = statement.replace(" ", "")
    return ((statement == "{t1}.{pk}={t2}.{fk}".format(t1=table_1_name,
                                                       t2=table_2_name,
                                                       pk=p_k,
                                                       fk=f_k))
            or (statement == "{t2}.{pk}={t1}.{fk}".format(t1=table_1_name,
                                                          t2=table_2_name,
                                                          pk=f_k,
                                                          fk=p_k)))


# function to determine if the table name is correct
def partial_order(input_, number):
    if number == 0:
        if order == 0:
            return(input_ == table_2_name)
        else:
            return(input_ == table_1_name)
    else:
        if order == 0:
            return(input_ == table_1_name)
        else:
            return(input_ == table_2_name)


# function to generate binary string as index for feedback
def feedback_list_index(rows, cols, join, name, name_):
    r, c, j, t1, t2 = int(rows is True), int(cols is True), int(join is True), \
        int(name is True), int(name_ is True)
    index = (format(((t2 << 4) | (t1 << 3) | (r << 2) | (c << 1) | j), '#07b'))
    index = index.replace('0b', '')
    return int(index), index


# function to verify that the table names are names
def verify_name(input_):
    if input_.split(" ", 2)[0] == table_1_name or input_.split(" ", 2)[0] == table_2_name:
        return True
    return False


# function to determine score for incorrect answers
def get_score(index):
    return (int(100 * (bin(index).count("1") / 5)) / 100.0)


# function to build queries used for partial credit grading for rows
def build_partial_query(pk, fk, condition):
    if order == 0:
        return "SELECT * FROM {t2} LEFT JOIN {t1} ON {t1}.{f_k} = {t2}.{p_k}"\
            .format(t1=table_2_name, t2=table_1_name, p_k=pk, f_k=fk) + condition
    else:
        return "SELECT * FROM {t1} LEFT JOIN {t2} ON {t1}.{p_k} = {t2}.{f_k}"\
            .format(t1=table_1_name, t2=table_2_name, p_k=pk, f_k=fk) + condition


# function to build queries used for partial credit grading for order of table names
def build_partial_order_query(input_, input__, condition, pk, fk):
    return "SELECT * FROM {t1} LEFT JOIN {t2} ON {t1_}.{p_k} = {t2_}.{f_k}"\
        .format(t1=input_, t2=input__, t1_=table_1_name, t2_=table_2_name,
                f_k=fk, p_k=pk) + condition


# function to build feedback message if the incorrect
def feedback_message(index):
    values = [int(d) for d in index]
    incorrect, correct = [], []
    incorrect_str, correct_str = "", ""

    # create string with incorrect & correct inputs
    if values[3] == 1:
        correct.append("the columns")
    else:
        incorrect.append("the columns")
    if values[0] == 1:
        correct.append("the first table name")
    else:
        incorrect.append("the first table name")
    if values[1] == 1:
        correct.append("the second table name")
    else:
        incorrect.append("the second table name")
    if values[4] == 1:
        correct.append("the join statement")
    else:
        incorrect.append("the join statement")
    if values[2] == 1:
        correct.append("the condition")
    else:
        incorrect.append("the condition")

    # generate substrings
    if len(correct) == 1:
        correct_str += correct[0]
    elif len(correct) == 2:
        correct_str = correct[0] + " & " + correct[1]
    else:
        for index in range(len(correct)):
            if index == len(correct) - 1:
                correct_str += " & " + correct[index]
            else:
                correct_str += correct[index] + ", "
    if len(incorrect) == 1:
        incorrect_str += incorrect[0]
    elif len(incorrect) == 2:
        incorrect_str = incorrect[0] + " & " + incorrect[1]
    else:
        for index in range(len(incorrect)):
            if index == len(incorrect) - 1:
                incorrect_str += " & " + incorrect[index]
            else:
                incorrect_str += incorrect[index] + ", "

    # return appropriate feedback messages
    if correct_str == "":
        return "All inputs were incorrect."
    return "The input(s) for " + correct_str + " were correct, but the input(s) for \
            " + incorrect_str + " were incorrect."


# function to build queries used for partial credit grading for join statement
def build_partial_join_query(t1_, t2_, join, condition):
    return "SELECT * FROM {t1} LEFT JOIN {t2} ON {j} {c}"\
        .format(t1=t1_, t2=t2_, j=join, c=condition)


# function that builds partial queries & calls partial helper grading function
def partial_grader(pk, fk, solution, data, solution_columns, student_columns):
    partial_answer = build_partial_query(pk, fk, " " + solution[solution.find("WHERE"):])
    student_partial_answer = build_partial_query(pk, fk, " WHERE " +
                                                 data["submitted_answers"]["condition"])
    if order == 0:
        partial_order_ = build_partial_order_query(table_2_name,
                                                   table_1_name,
                                                   " " + solution[solution.find("WHERE"):],
                                                   pk,
                                                   fk)
        partial_join_ = build_partial_join_query(table_2_name, table_1_name, "{t1}.{p_k}\
                ={t2}.{f_k}".format(t1=table_1_name,
                                    t2=table_2_name,
                                    p_k=pk,
                                    f_k=fk), " " + solution[solution.find("WHERE"):])
    else:
        partial_order_ = build_partial_order_query(table_1_name,
                                                   table_2_name,
                                                   " " + solution[solution.find("WHERE"):],
                                                   pk,
                                                   fk)
        partial_join_ = build_partial_join_query(table_1_name,
                                                 table_2_name,
                                                 "{t1}.{p_k}={t2}.{f_k}".format(t1=table_1_name,
                                                                                t2=table_2_name,
                                                                                p_k=pk,
                                                                                f_k=fk),
                                                 " " + solution[solution.find("WHERE"):])
    student_partial_join_ = build_partial_join_query(data["submitted_answers"]["table_1"],
                                                     data["submitted_answers"]["table_2"],
                                                     data["submitted_answers"]["on"],
                                                     " " + solution[solution.find("WHERE"):])
    student_partial_order_ = build_partial_order_query(data["submitted_answers"]["table_1"].split(" ", 2)[0],
                                                       data["submitted_answers"]["table_2"].split(" ", 2)[0],
                                                       " " + solution[solution.find("WHERE"):],
                                                       pk,
                                                       fk)
    return partial_helper(partial_answer,
                          student_partial_answer,
                          partial_order_,
                          partial_join_,
                          student_partial_join_,
                          student_partial_order_,
                          data,
                          solution_columns,
                          student_columns,
                          pk,
                          fk)


# function to determine partial credit for join statement if aliases are used
def partial_join_alias(pk, fk, statement, data, one, two):
    statement = statement.replace(" ", "")
    if one != -1:
        input_1_table_name = data["submitted_answers"]["table_1"].split(" ")[0]
        input_1_alias = data["submitted_answers"]["table_1"].split(" ")[1]
    else:
        input_1_table_name = data["submitted_answers"]["table_1"]
        input_1_alias = "ALIAS DNE"
    if two != -1:
        input_2_table_name = data["submitted_answers"]["table_2"].split(" ")[0]
        input_2_alias = data["submitted_answers"]["table_2"].split(" ")[1]
    else:
        input_2_table_name = data["submitted_answers"]["table_2"]
        input_2_alias = "ALIAS DNE"
    if input_1_table_name == table_1_name:
        parent = 1
    elif input_2_table_name == table_1_name:
        parent = 2
    else:
        return False
    if parent == 1:
        if input_1_alias != "ALIAS DNE":
            if input_2_alias != "ALIAS DNE":
                return ((statement == "{t1}.{pk_}={t2}.{fk_}".format(t1=input_1_alias,
                                                                     t2=input_2_alias,
                                                                     pk_=pk,
                                                                     fk_=fk))
                        or (statement == "{t1}.{pk_}={t2}.{fk_}".format(t1=input_2_alias,
                                                                        t2=input_1_alias,
                                                                        pk_=fk,
                                                                        fk_=pk)))
            else:
                return ((statement == "{t1}.{pk_}={t2}.{fk_}".format(t1=input_1_alias,
                                                                     t2=input_2_table_name,
                                                                     pk_=pk,
                                                                     fk_=fk))
                        or (statement == "{t1}.{pk_}={t2}.{fk_}".format(t1=input_2_table_name,
                                                                        t2=input_1_alias,
                                                                        pk_=fk,
                                                                        fk_=pk)))
        else:
            return ((statement == "{t1}.{pk_}={t2}.{fk_}".format(t1=input_1_table_name,
                                                                 t2=input_2_alias,
                                                                 pk_=pk,
                                                                 fk_=fk))
                    or (statement == "{t1}.{pk_}={t2}.{fk_}".format(t1=input_2_alias,
                                                                    t2=input_1_table_name,
                                                                    pk_=fk,
                                                                    fk_=pk)))
    else:
        if input_1_alias != "ALIAS DNE":
            if input_2_alias != "ALIAS DNE":
                return ((statement == "{t1}.{pk_}={t2}.{fk_}".format(t1=input_2_alias,
                                                                     t2=input_1_alias,
                                                                     pk_=pk,
                                                                     fk_=fk))
                        or (statement == "{t1}.{pk_}={t2}.{fk_}".format(t1=input_1_alias,
                                                                        t2=input_2_alias,
                                                                        pk_=fk,
                                                                        fk_=pk)))
            else:
                return ((statement == "{t1}.{pk_}={t2}.{fk_}".format(t1=input_2_table_name,
                                                                     t2=input_1_alias,
                                                                     pk_=pk,
                                                                     fk_=fk))
                        or (statement == "{t1}.{pk_}={t2}.{fk_}".format(t1=input_1_alias,
                                                                        t2=input_2_table_name,
                                                                        pk_=fk,
                                                                        fk_=pk)))
        else:
            return ((statement == "{t1}.{pk_}={t2}.{fk_}".format(t1=input_2_alias,
                                                                 t2=input_1_table_name,
                                                                 pk_=pk,
                                                                 fk_=fk))
                    or (statement == "{t1}.{pk_}={t2}.{fk_}".format(t1=input_1_table_name,
                                                                    t2=input_2_alias,
                                                                    pk_=fk,
                                                                    fk_=pk)))


# function that determines score and message given partial queries
def partial_helper(partial_answer,
                   student_partial_answer,
                   partial_order_,
                   partial_join_,
                   student_partial_join_,
                   student_partial_order_,
                   data,
                   solution_columns,
                   student_columns,
                   pk,
                   fk):
    student_columns_for_partial = student_columns.copy()
    try:
        sol_j, stu_j = grade_helper(partial_join_, 1), grade_helper(student_partial_join_, 1)
        if(sol_j == stu_j):
            join_matching = True
        else:
            one, two = data["submitted_answers"]["table_1"].find(" "), data["submitted_answers"]["table_2"].find(" ")
            if one != -1 or two != -1:
                join_matching = partial_join_alias(pk, fk, data["submitted_answers"]["on"], data, one, two)
            else:
                join_matching = partial_join(pk, fk, data["submitted_answers"]["on"])
    except Exception:
        join_matching = False
    try:
        vn1, vn2 = verify_name(data["submitted_answers"]["table_1"]), verify_name(data["submitted_answers"]["table_2"])
        if vn1 and vn2:
            sol_oc, stu_oc = grade_helper(partial_order_, 1), grade_helper(student_partial_order_, 1)
            if sol_oc == stu_oc:
                table_one_matching, table_two_matching = True, True
            else:
                table_one_matching = partial_order(data["submitted_answers"]["table_1"].split(" ")[0], 0)
                table_two_matching = partial_order(data["submitted_answers"]["table_2"].split(" ")[0], 1)
        else:
            table_one_matching = partial_order(data["submitted_answers"]["table_1"].split(" ")[0], 0)
            table_two_matching = partial_order(data["submitted_answers"]["table_2"].split(" ")[0], 1)
    except Exception:
        table_one_matching, table_two_matching = False, False
    row_matching = partial_rows(partial_answer, student_partial_answer)
    column_matching = partial_cols(solution_columns, student_columns_for_partial)
    index, index_str = feedback_list_index(row_matching, column_matching, join_matching,
                                           table_one_matching, table_two_matching)
    return get_score(int(str(index), 2)), feedback_message(index_str)


def grade(data):
    # indicate arrival in grade function
    data["correct_answers"]["flag"], solution = 1, data["params"]["solution"]
    pk, fk = data["params"]["primary_key"], data["params"]["foreign_key"]
    student_answer = "SELECT " + data["submitted_answers"]["columns"] + " FROM " + \
        data["submitted_answers"]["table_1"] + " LEFT JOIN " + data["submitted_answers"]["table_2"] \
        + " ON " + data["submitted_answers"]["on"] + " WHERE " + data["submitted_answers"]["condition"]

    # check student solution and assign scores & feedback appropriately
    solution_columns, data1 = grade_helper(solution, 0)
    student_columns, data2 = grade_helper(student_answer, 0)
    # student_columns_for_partial = student_columns.copy()
    if(data1 == data2):
        data["score"], data["feedback"]["message"] = 1, "Correct!"
    else:
        data["score"], data["feedback"]["message"] = \
                partial_grader(pk, fk, solution, data, solution_columns, student_columns)

    # add appropriate data for feedback
    data["feedback"]["student_results"] = get_table_data(student_answer)
    data["feedback"]["columns_s"] = student_columns

    return data
