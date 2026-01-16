import chevron
import re
import lxml.html
import prairielearn as pl
import json
import grading.grading as grading
import os, contextlib

# maybe issue is in info.json? check documentation

def generate(element_html, data):
    pass

def prepare(element_html, data):
    element = lxml.html.fragment_fromstring(element_html)
    if data["params"]["codestring"] == "Question generation failed. Question file may be malformed.":
        # TODO: add handling
        pass
    data['params']['granularity'] = int(element.get("granularity") or 1)
    for sub_element in element.iter():
        if sub_element.tag == "base-code":
            base_code = sub_element.text
            data["correct_answers"] = post_process_data(grading.get_correctAnswerJSON(base_code))
    return data

def is_number_str(str):
    for char in str:
        if not('0' <= char <= '9'):
            return False
    return True

def unflatten_raw_data(raw_data, special_keys=()):
        """
        Special keys means you stop processing the tree at that point.
        >>> raw_data = {'frame-0-var-0-name': 'x', 'frame-0-var-0-val': '5', 'frame-0-var-NaN-name': 'y', 'frame-0-var-NaN-val': '17', 'frame-1-name': 'g', 'frame-1-parent': 'Global', 'frame-1-var-0-name': 'z', 'frame-1-var-0-val': '"hi"', 'frame-1-return-val': '3'}
        >>> Frame.unflatten_raw_data(raw_data)
        {'frame': [{'index': '0', 'var': [{'index': '0', 'name': 'x', 'val': '5'}, {'index': '2', 'name': 'y', 'val': '17'}]}, {'index': '1', 'name': 'g', 'parent': 'Global', 'return': {'val': '3'}, 'var': [{'index': '0', 'name': 'z', 'val': '"hi"'}]}]}
        """
        parsed_response = {}
        
        for key, value in sorted(raw_data.items(), key=lambda x: x[0]):
            key_components = key.split("-")
            prev = None
            prev_key = None
            prev_dict_key = None
            vanguard = parsed_response
            for i, component in enumerate(key_components):
                if vanguard is None:
                    if is_number_str(component):
                        vanguard = []
                    else: 
                        vanguard = {}
                    if type(prev) == dict:
                        prev[prev_key] = vanguard
                    elif type(prev) == list:
                        vanguard[prev_dict_key + 'Index'] = prev_key
                        prev.append(vanguard)

                prev = vanguard

                if prev_key in special_keys:
                    break

                prev_key = component
                if not is_number_str(prev_key):
                    prev_dict_key = prev_key

                if type(vanguard) == dict and component in vanguard: 
                    vanguard = vanguard[component]
                elif type(vanguard) == list and vanguard and vanguard[-1][prev_dict_key + 'Index'] == component:
                    vanguard = vanguard[-1]
                else: 
                    vanguard = None
            
            if type(prev) == dict:
                prev["-".join(key_components[i:])] = value
            elif type(prev) == list:
                prev.append(value)

        return parsed_response

def post_process_data(parsed_response):
    '''Adds data necessary for rendering'''
    if 'frame' not in parsed_response:
        parsed_response['frame'] = [default_global_frame]

    pointer_list = []
    def process(key, obj, history, parent):
            if key == 'item' and type(obj) == list and obj:
                obj[-1]["isLastElement"] = True

            elif (key == 'val' or key == 'name') and type(obj) == str: # Injecting lengths and pointer information
                if key == 'val' and obj and obj[0] == '#':
                    #print(structured_answers)
                    origin = "-".join(history)
                    if 'pointer' in parsed_response: 
                        raw_pointer_data = parsed_response['pointer'][origin+"-input"]
                        pointer_data = json.loads(raw_pointer_data)
                        pointer_data.update({'origin': origin, 'destination': obj[1:], 'raw': raw_pointer_data})
                        pointer_list.append(pointer_data)
                    else: # In this case, no pointer has been rendered. A bunch of blank pointers will be rendered for the front end to render. 
                        pointer_list.append({
                            "d": "M 0, 0 L 0 0",
                            "raw": '{"d":"M 0, 0 L 0 0","width":"0","height":"0","top":"0px","left":"0px"}',
                            "top": "0px",
                            "left": "0px",
                            "width": "0",
                            "height": "0",
                            "origin": origin,
                            "destination": obj[1:],
                        })
                else: 
                    parent[key + 'Width'] = len(obj) + 1

    def investigate(key, obj, history, parent):
        process(key, obj, history, parent)
        if type(obj) == list:
            for item in obj:
                investigate(item[key + "Index"], item, history + [str(item[key + "Index"])], obj)
        elif type(obj) == dict:
            for child_key, child in dict(obj).items():
                investigate(child_key, child, history + [child_key], obj)

    investigate(None, parsed_response, [], None)
    parsed_response['pointer'] = pointer_list
    return parsed_response


def parse(element_html, data):
    if not data["submitted_answers"]:
        data['submitted_answers'] = default_submission
    structured_answers = unflatten_raw_data(data["submitted_answers"], ('pointer',))
    structured_answers = post_process_data(structured_answers)
    data['submitted_answers'] = structured_answers
    return data

default_global_frame = {'name': None, 'frameIndex': 0, 'var': [], 'parent': None}
default_submission = {'frame': [default_global_frame], 'heap': {}}
def render(element_html, data):
    with open("editor.mustache", "r") as f:
        template = f.read()
        if data['panel'] == 'answer':
            rendering_data = data['correct_answers']
            show_controls = False
        elif data['panel'] == 'question': 
            rendering_data = data['submitted_answers']
            show_controls = True
        else: # Submission
            rendering_data = data['submitted_answers']
            show_controls = False
        if not rendering_data:
            rendering_data = default_submission
        rendering_data.update({'show_controls': show_controls})
        return chevron.render(template, rendering_data)

def grade(element_html, data):
    score, feedback = grading.grading(data['correct_answers'], data['submitted_answers'], granularity=data['params']['granularity'])
    if score is None:
        gradable = False
    else:
        gradable = True
    data['partial_scores']['problem'] = {'score': score,
                                    'feedback': feedback,
                                    'weight':1,
                                    'gradable':gradable}
