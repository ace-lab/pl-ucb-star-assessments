import prairielearn as pl
import json
import chevron
import lxml.html


ALLOW_SELFLINKS_DEFAULT = True
MULTIGRAPH_DEFAULT = True
ALLOW_NODEMARKING_DEFAULT = True

def prepare(element_html, data):
    element = lxml.html.fragment_fromstring(element_html)
    required_attribs = ["directed"]
    optional_attribs = ["allow-selflinks", "multigraph", "allow-nodemarking"]
    
    pl.check_attribs(element, required_attribs, optional_attribs)
    

def render(element_html, data):
    # Render the Mustache template using chevron
    #return chevron.render(element_html, {}).strip()
    element = lxml.html.fragment_fromstring(element_html)
    directed = pl.get_boolean_attrib(element, "directed")
    allow_selflinks = pl.get_boolean_attrib(element, "allow-selflinks", ALLOW_SELFLINKS_DEFAULT)
    multigraph = pl.get_boolean_attrib(element, "multigraph", ALLOW_SELFLINKS_DEFAULT)
    allow_nodemarking = pl.get_boolean_attrib(element, "allow-nodemarking", ALLOW_NODEMARKING_DEFAULT)

    config = {
        'directed': "true" if directed else "false",
        'allow_selflinks': "true" if allow_selflinks else "false",
        'multigraph': "true" if multigraph else "false",
        'allow_nodemarking': "true" if allow_nodemarking else "false"
    }
    
    with open('pl-graph-constructor.mustache', 'r') as f:
        return chevron.render(f, {'config': config}).strip()

def parse(element_html, data):
    graph_data = data['submitted_answers'].get('graphData', '')
    data['submitted_answers']['graphData'] = graph_data




