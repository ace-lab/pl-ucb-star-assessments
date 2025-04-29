import chevron
import lxml
import json
import base64
import prairielearn as pl
import os

DIRECTORY_DEFAULT = "clientFilesQuestion"
SOURCE_FILE_NAME_DEFAULT = None

def render(element_html, data):
    element = lxml.html.fragment_fromstring(element_html)

    source_file_name = pl.get_string_attrib(
        element, "source-file-name", SOURCE_FILE_NAME_DEFAULT
    )
    directory = pl.get_string_attrib(element, "directory", DIRECTORY_DEFAULT)
    default_file = None
    
    if source_file_name is not None:
        if directory == "serverFilesCourse":
            directory = data["options"]["server_files_course_path"]
        elif directory == "clientFilesCourse":
            directory = data["options"]["client_files_course_path"]
        else:
            directory = os.path.join(data["options"]["question_path"], directory)
        file_path = os.path.join(directory, source_file_name)
        xml_file = open(file_path, "r", encoding="utf-8")
        default_file = xml_file.read()
        xml_file.close()

    submitted_files = data["submitted_answers"].get("_files", [])

    if default_file:
        default_file = base64.b64encode(default_file.encode()).decode()
    
    student_submission = None
    for file in submitted_files:
        if file["name"] == "submission.xml":
            student_submission = file["contents"]
            break
    html_params = {
        "student_submission": student_submission if student_submission else default_file
}
    with open("pl-snap.mustache", "r") as f:
        return chevron.render(f, html_params).strip()
    
def parse(element_htm, data):

    submission = data["submitted_answers"]["submission.xml"]
    if (not submission):
        data["format_errors"]["files"] = "submission.xml is required"
        return
    
    if data["submitted_answers"].get("_files", None) is None:
        data["submitted_answers"]["_files"] = []

    for file in data["submitted_answers"]["_files"]:
        if file["name"] == "submission.xml":
            data["submitted_answers"]["_files"].remove(file)
            break
    
    data["submitted_answers"]["_files"].append({
        "name" : "submission.xml",
        "contents" : base64.b64encode(data["submitted_answers"]["submission.xml"].encode()).decode()
    })