import random
import math
import json
from typing import TypedDict

import chevron
import lxml.html
import prairielearn as pl
class GridAnswerData(TypedDict):
    x: int
    y: int
    w: int
    h: int
    content: str

def prepare(element_html, data):
    element = lxml.html.fragment_fromstring(element_html)

    correct_answers: list[GridAnswerData] = []
    source_blocks: list[GridAnswerData] = []
    given_blocks: list[GridAnswerData] = []
    color_map: dict = {}

    for html_tags in element:
        if html_tags.tag == "pl-answer-grid":
            for inner_tag in html_tags:
                if inner_tag.tag == "pl-element":
                    answer_data_dict: GridAnswerData = {
                        "x": int(inner_tag.get("x", 100)),
                        "y": int(inner_tag.get("y", 100)),
                        "w": int(inner_tag.get("w", 2)),
                        "h": int(inner_tag.get("h", 1)),
                        "content": inner_tag.text_content().strip()
                    }
                    correct_answers.append(answer_data_dict)
        elif html_tags.tag == "pl-destination":
            for inner_tag in html_tags:
                if inner_tag.tag == "pl-element":
                    content = inner_tag.text_content().strip()
                    given_block_dict: GridAnswerData = {
                        "x": int(inner_tag.get("x", 100)),
                        "y": int(inner_tag.get("y", 100)),
                        "w": int(inner_tag.get("w", 2)),
                        "h": int(inner_tag.get("h", 1)),
                        "content": content
                    }
                    given_blocks.append(given_block_dict)
                    color = inner_tag.get("color", "#ffffff")
                    color_map[content] = color
        elif html_tags.tag == "pl-source":
            for inner_tag in html_tags:
                if inner_tag.tag == "pl-element":
                    content = inner_tag.text_content().strip()
                    source_block_dict: GridAnswerData = {
                        "x": int(inner_tag.get("x", 100)),
                        "y": int(inner_tag.get("y", 100)),
                        "w": int(inner_tag.get("w", 2)),
                        "h": int(inner_tag.get("h", 1)),
                        "content": content
                    }
                    source_blocks.append(source_block_dict)
                    color = inner_tag.get("color", "#ffffff")
                    color_map[content] = color
    
    color_column = element.get("color-column", "false").lower() == "true"

    data["correct_answers"]["test"] = correct_answers
    data["params"]["test"] = { "source": source_blocks, "given": given_blocks, "colors": color_map, "color_column": color_column}

def render(element_html, data):
    if data["panel"] == "question":
        html_params = {
            "question": True,
            "load_data": json.dumps(data["params"]["test"])
        }
        with open('pl-grid.mustache', 'r') as f:
            return chevron.render(f, html_params).strip()
        
    elif data["panel"] == "submission":
        all_submissions = data["submitted_answers"].get("test", [])

        html_params = {
            "submission": True,
            "student_submission": [
                {"load_data_sub": json.dumps(sub)} for sub in all_submissions
            ]
        }

        with open('pl-grid.mustache', 'r') as f:
            return chevron.render(f, html_params).strip()

        
    elif data["panel"] == "answer":
        html_params = {
            "true_answer": True,
            "load_data_sol": json.dumps(data["correct_answers"].get("test", []))
        }
        with open('pl-grid.mustache', 'r') as f:
            return chevron.render(f, html_params).strip()
    

def parse(element_html, data):
    new_submission = json.loads(data["raw_submitted_answers"].get("test-input", "[]"))
    
    # Initialize as list of submissions if not already
    if "test" not in data["submitted_answers"]:
        data["submitted_answers"]["test"] = []

    data["submitted_answers"]["test"].append(new_submission)


def grade(element_html, data):
    given = data["params"]["test"]["given"]
    correct_answers = data["correct_answers"]["test"]
    all_submissions = data["submitted_answers"]["test"]

    submitted = all_submissions[-1]
    full_score_possible = len(correct_answers) - len(given)
    correct_cells = 0

    for cell in submitted:
        cell["x"] = int(cell["x"])
        cell["y"] = int(cell["y"])
        cell["w"] = int(cell["w"])
        cell["h"] = int(cell["h"])

        if (cell in correct_answers):
            correct_cells += 1
        
    if full_score_possible > 0:
        score = (correct_cells - len(given)) / full_score_possible
        score = max(score, 0)  # don't allow negative scores
    else:
        score = 0

    if score >= 0.99:
        score = 1
    
    data["partial_scores"]["test"] = {
        "score": score,
        "feedback": f"{correct_cells} out of {full_score_possible} cells matched.",
    }