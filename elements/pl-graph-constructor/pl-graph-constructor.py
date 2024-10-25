import prairielearn as pl
import json
import chevron

def render(element_html, data):
    # Render the Mustache template using chevron
    #return chevron.render(element_html, {}).strip()
    with open('pl-graph-constructor.mustache', 'r') as f:
        return chevron.render(f).strip()

def parse(element_html, data):
    graph_data = data['submitted_answers'].get('graphData', '')
    data['submitted_answers']['graphData'] = graph_data

def grade(element_html, data):
    # Implement grading logic here
    # For now, we'll give full credit for any submission
    data['score'] = 1
    student_dot = data['submitted_answers'].get('graphData', '')
    print(student_dot)


