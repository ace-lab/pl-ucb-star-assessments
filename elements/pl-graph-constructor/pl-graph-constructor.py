import prairielearn as pl
import json
import chevron
import lxml.html
import re


ALLOW_SELFLINKS_DEFAULT = True
MULTIGRAPH_DEFAULT = True
ALLOW_NODEMARKING_DEFAULT = True

def prepare(element_html, data):
    element = lxml.html.fragment_fromstring(element_html)
    required_attribs = ["directed", "answers-name"]
    optional_attribs = ["allow-selflinks", "multigraph", "allow-nodemarking"]
    
    pl.check_attribs(element, required_attribs, optional_attribs)
    

def render(element_html, data):
    # Render the Mustache template using chevron
    #return chevron.render(element_html, {}).strip()
    element = lxml.html.fragment_fromstring(element_html)
    directed = pl.get_boolean_attrib(element, "directed")
    answers_name = pl.get_string_attrib(element, "answers-name")
    if not re.match(r'^[A-Za-z0-9_]+$', answers_name):
        raise ValueError("answers-name can only contain alphabetic characters, numbers and underscores.")
    allow_selflinks = pl.get_boolean_attrib(element, "allow-selflinks", ALLOW_SELFLINKS_DEFAULT)
    multigraph = pl.get_boolean_attrib(element, "multigraph", ALLOW_SELFLINKS_DEFAULT)
    allow_nodemarking = pl.get_boolean_attrib(element, "allow-nodemarking", ALLOW_NODEMARKING_DEFAULT)

    config = {
        'answers_name': answers_name,
        'directed': "true" if directed else "false",
        'allow_selflinks': "true" if allow_selflinks else "false",
        'multigraph': "true" if multigraph else "false",
        'allow_nodemarking': "true" if allow_nodemarking else "false"
    }
        
    with open('pl-graph-constructor.mustache', 'r') as f:
        return chevron.render(f, {'config_py': config}).strip()

def parse(element_html, data):
    graph_data = data['submitted_answers'].get('graphData', '')
    data['submitted_answers']['graphData'] = graph_data




