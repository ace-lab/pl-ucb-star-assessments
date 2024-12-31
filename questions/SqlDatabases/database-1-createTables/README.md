# Welcome to Build-A-Table

This is a question on SQL CREATE statements that tests students ability to write a SQL query to create a given table.

## Example

<img src="../../../clientFilesCourse/database-1-createTables-images/questionvariant.png">

## Notes

We create and grade this question using the python `sqlite3` library. We execute the student's query then compare it to the expected result.

The table name is a randomly generated string of fixed length. The column names are taken randomly from faker.csv and the types are randomly assigned, allowing for immense randomization for the question.

To help students understand where they are going wrong if they make a mistake, we display the actual output of their SQL query in the submission panel. Below is an example.
<img src="../../../clientFilesCourse/database-1-createTables-images/incorrectanswer.png">

If there is a syntax error, the student is told so and given the error in the submission panel. Below is an example
<img src="../../../clientFilesCourse/database-1-createTables-images/invalidanswer.png">

### Contact karthiksreedhar@berkeley.edu (Github: karthiksreedhar) or find Karthik Sreedhar on Slack for questions
