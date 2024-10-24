import prairielearn as pl
import json
import chevron

# def generate(element_html, data):
#     # No parameters to generate unless you have initial graph data
#     pass

# def prepare(element_html, data):
#     # No additional preparation needed
#     pass


def render(element_html, data):
    # Render the Mustache template using chevron
    #return chevron.render(element_html, {}).strip()
    with open('pl-graph-constructor.mustache', 'r') as f:
        return chevron.render(f).strip()


# def parse(element_html, data):
#     # Retrieve the student's submitted graph data
#     graph_data_json = data['raw_submitted_answers'].get('graphData', '{}')
#     data['submitted_answers']['graphData'] = graph_data_json

# def grade(element_html, data):
#     # Implement grading logic here
#     # For now, we'll give full credit for any submission
#     data['score'] = 1
#     data['partial_scores']['graph'] = {'score': 1, 'weight': 1}

# # def test(element_html, data):
# #     # For testing purposes, you can set up test submissions
# #     pass
