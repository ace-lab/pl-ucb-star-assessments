import random


def generate(data):
    data["params"]["dot_notation"] = "Your dot notation here"

def grade(data):
    correct_answer = "AB"
    student_answer = data["submitted_answers"]["user_answer"]
    score = 0
    for j in range(min(len(correct_answer), len(student_answer))):
        if correct_answer[j] == student_answer[j]:
            score += 1
    data["score"] = score/(max(len(student_answer), len(correct_answer)))