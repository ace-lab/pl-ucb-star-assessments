import random


def generate(data):
    data["params"]["dot_notation"] = "Your dot notation here"

def grade(data):
    correct_answer = {'D--G', 'E--H', 'B--C', 'G--H', 'H--I', 'A--B', 'C--F'}
    student_answer = data["submitted_answers"]["user_answer"]

    # Normalize the student's answer by removing leading/trailing whitespaces and converting to upper case
    # Split the answer at commas, strip extra whitespace, and remove any quotes just in case
    edges_list = set(edge.strip().replace('"', '').replace("'", "").upper() for edge in student_answer.split(","))

    # Calculate the score based on the intersection of the student's answers and the correct answers
    score = len(correct_answer.intersection(edges_list))

    # Assign the score proportionally based on the correct answer length
    data["score"] = score / len(correct_answer)
