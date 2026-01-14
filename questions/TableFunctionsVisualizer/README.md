# Guide to the Table Operations Practice question!
Welcome. This question is geared towards data science beginners, such as current Data C8 / Data 6 students, with an emphasis on learning, visualizing, and experimenting with several Data 8 table operations and methods! 

This question utilizes a dataset from the Data 8 textbook that was collected to help doctors diagnose chronic kidney disease. Some example columns include 'Age' and 'Blood Pressure.' Our goal in designing this question is to create a tool, within PrairieLearn, that allows students to visualize popular table operations and how they work in unison. Our hope is that this question will be used in formative assessments. 

# Getting started
The server.py generate() function will take in the CSV file and randomly select one categorical and one numerical column. Then, it will also randomly select from 3 types of operations: WHERE, SORT, and SELECT. There will be additional randomness depending on which of the 3 operations the function selects. 

This information will also be saved in the grading parameters, so students are able to check their work and see their score. 

As for what instructors have to do, they can opt out of the manual random selections. 

# How it will support learning
With this tool, students are given a way to practice common Data 8 table operations. We chose to limit the first operation to a .group because this operation is one of the hardest to master (based on our teaching experience). We expect students to read the question, notice that the solution involves a .group, and experiment with the visualizer tool to see how they can curate and collect the data to answer the prompt. Students can try new and unique variants given the randomness of the question. Plus, the visualizer isn't graded -- only their final response is -- so they are free to use the tool as little or as much as they prefer. 

You may wonder if similar tools already exist. This is different from the existing Data 8 table function visualizer tool (https://www.data8.org/interactive_table_functions/) in several ways. First, the existing tool only includes 'group' and 'pivot' functions with two given tables (chocolates and cones). Students may have a hard time bridging the gap between those two tables and newer, larger datasets. With our tool, it gives students a chance to visualize a larger dataset, one that is more relevant to their HW and assessments. Our tool also gives students the chance to try conjoined operations (>1 operation). Students will link a .group function with a .sort, .where, or a .select, and be able to visualize the output of two joined functions! 





