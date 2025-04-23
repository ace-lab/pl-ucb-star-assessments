import random
import chevron
import lxml.html
import prairielearn as pl

def prepare(element_html, data):
    element = lxml.html.fragment_fromstring(element_html)
    function = pl.get_string_attrib(element, 'function')
    data['params']['function'] = function
    return data

def render(element_html, data):
    html_params = {
        'function': data['params']['function']
    }
    with open('pl-interactive-visualizer.mustache', 'r') as f:
        return chevron.render(f, html_params).strip()
