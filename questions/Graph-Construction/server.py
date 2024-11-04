def grade(data):
    correct_answer = "digraphG{N0[label=\"A\",shape=circle];N1[label=\"B\",shape=circle];N0->N1[label=\"\"];}"

    # Get the student's answer, remove spaces and newlines
    student_dot = data['submitted_answers'].get('graphData', '')
    cleaned_student_dot = ''.join(student_dot.split())

    # Check if the student's answer matches the correct answer
    if cleaned_student_dot == correct_answer:
        data['score'] = 1  # Full credit
    else:
        data['score'] = 0  # No credit
