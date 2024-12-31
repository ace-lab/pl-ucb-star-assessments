# Come Join Us

This is a question on SQL two table queries that tests students abiity to write SQL queries to return a specified subset of rows & columns from given parent and child tables.

## Example

<img src="../../../clientFilesCourse/database-2-inputSQL-images/questionvariant.png">

## Notes

The information for varaint tables & queries can be inputted into the file table.json which can be found in the clientFilesCourse folder of the repository. The file contains a list of lists that contain JSON elements, each representing a table. Each sublist must contain at least one parent table and one child table, specified by the existence or lack of a foreign key associated with the parent table's primary key. Each JSON element in the sublists must have the following specified keys.
* table_name - name of the table as a string
* columns - list of column names as strings
* create - valid SQL create statement to create the intended table that clearly specifies primary keys, and foreign keys when appropriate
* rows - list of lists, each sublist (representative of a row) containing the values for each column
* condtions - list of strings that begin with "WHERE" and specificy an appropriate and valid condition for potential SQL queries for the table created

If a column is also found in faker.csv, put row elements as `Fake <column_name>` in table.json. Server.py will automatically populate such rows with potential values. Similarly, conditions can be set as "WHERE column_name = '`Fake <column_name>`'" to be populated with random faker data for a column in the table to be randomized.

We create and grade this question using the python `sqlite3` library. We apply the student's query to the given tables and compare it to the expected result. Some questions have multiple correct answers, all of which will be accepted.

The primary key & foreign key of the respective tables are specified to the student, as is which the parent & child table are.

The server python file has many helper functions, many of which are also utilized in other database questions. Hence, this allowed for the generate(), parse(), and grade() functions to be relatively similar between the different question types.

The student answer interface was divided into three input boxes in order to reduce potential errors in syntax of SQL and also allow for partial credit to be given. Students can be given partial credit for correctly answering one or two of the necessary inputs, as opposed to being marked wrong altogether due to an error in one or two of the inputs. The only exception is when there are clear syntax errors in any of the answer inputs, as the input format already significantly reduces the risk of pure syntactical errors. Below are examples of partial credit being given.
<img src="../../../clientFilesCourse/database-2-inputSQL-images/partialcredit-1.png">
<img src="../../../clientFilesCourse/database-2-inputSQL-images/partialcredit-2.png">

The order in which students select columns does not matter, as long as the correct columns are selected.

To help students understand where they are going wrong if they make a mistake, we display the actual output of their SQL query in the submission panel. Below is an example.
<img src="../../../clientFilesCourse/database-2-inputSQL-images/incorrectanswer.png">

If the student answer has a synctatical error, the specific error is displayed to the student. Below is an example.
<img src="../../../clientFilesCourse/database-2-inputSQL-images/invalidanswer.png">

One limitation of this question is that variants must be created by the instructor in table.json. This was done because complete randomization of tables & queries was less feasible as it was difficult to generate appropriate queries with conditions that would make sense for the particular table variant chosen.

### Contact karthiksreedhar@berkeley.edu (Github: karthiksreedhar) or find Karthik Sreedhar on Slack for questions
