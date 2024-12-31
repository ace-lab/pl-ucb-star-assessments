# Query Me This

This is a question on SQL single table queries that tests students abiity to write SQL queries to return a specified subset of rows & columns from a given table.

## Example

<img src="../../../clientFilesCourse/database-1-inputSQL-images/questionvariant.png">

## Notes

The information for varaint tables & queries can be inputted into the file table.json found in the clientFilesCourse folder of the repository. There are currently three tables, but more can be added as needed. Tables can contain any number of rows and columns. To add a table, create another JSON element in the file that includes the following keys:
* table_name - the name of the desired table as a string
* columns - list of column names as strings
* queries - list of complete AND valid SQL queries that could be applied to the table
* create - valid SQL create statement to create the intended table
* rows - list of lists, each sublist (representative of a row) containing the values for each column

If a column is also found in faker.csv, put row elements as `Fake <column_name>` in table.json. Server.py will automatically populate such rows with potential values. Similarly, conditions can be set as "WHERE column_name = '`Fake <column_name>`'" to be populated with random faker data for a column in the table to be randomized.

We create and grade this question using the python `sqlite3` library. We apply the student's query to the given table and compare it to the expected result. Some questions have multiple correct answers, all of which will be accepted.

In order to make it more difficult students to merely select the appropriate rows using the trivial solution (i.e. specifying a value for one column for every necessary row), no id column was given. Although the trivial solution is still possible using another column, it is significantly more difficult and time-consuming to enter than a more simple, expected solution.

The server python file has many helper functions, many of which are also utilized in other database questions. Hence, this allowed for the generate(), parse(), and grade() functions to be relatively similar between the different question types.

The student answer interface was divided into two input boxes in order to reduce potential errors in syntax of SQL and also allow for partial credit to be given. Students can be given partial credit for correctly selecting only columns or rows, as opposed to being marked wrong altogether due to an error in one input. The only exception is when there are clear syntax errors in either of the answer inputs, as the input format already significantly reduces the risk of pure syntactical errors. Below are examples of partial credit being given.
<img src="../../../clientFilesCourse/database-1-inputSQL-images/partialcredit-1.png">
<img src="../../../clientFilesCourse/database-1-inputSQL-images/partialcredit-2.png">

The order in which students select columns does not matter, as long as the correct columns are selected.

To help students understand where they are going wrong if they make a mistake, we display the actual output of their SQL query in the submission panel. Below is an example.
<img src="../../../clientFilesCourse/database-1-inputSQL-images/incorrectanswer.png">

If there is a syntax error, the student is told so in the submission panel. Below is an example.
<img src="../../../clientFilesCourse/database-1-inputSQL-images/invalidanswer.png">

One limitation of this question is that variants must be created by the instructor in table.json. This was done because complete randomization of tables & queries was less feasible as it was difficult to generate appropriate queries with conditions that would make sense for the particular table variant chosen.

### Contact karthiksreedhar@berkeley.edu (Github: karthiksreedhar) or find Karthik Sreedhar on Slack for questions
