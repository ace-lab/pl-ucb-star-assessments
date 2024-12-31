from typing import cast
import chevron
import lxml.html
import json
import pandas as pd
import prairielearn as pl
from bs4 import BeautifulSoup

DEFAULT_STRING_COLUMN = "Choose answer column here"
DEFAULT_STRING_INDEX = "Choose answer index here"
DEFAULT_STRING_ROW = "Choose answer row here"
DEFAULT_STRING_DROP = "Drop your answer here"

def prepare(element_html, data):
    soup = BeautifulSoup(element_html)

    drop_label = soup.find('pl-pivot-table')['dropzone'][0] if soup.find('pl-pivot-table').has_attr("dropzone") else False
    
    num_col = int(soup.find('pl-pivot-table')['col'])
    if num_col < 2:
        print("Invalid column number")
    data['params']['num_col'] = num_col
    
    num_row = int(soup.find('pl-pivot-table')['row'])
    if num_row < 1:
        print("Invalid row number")
    data['params']['num_row'] = num_row
    
    #num_index won't be refered in this function again, so there is no declaration of it
    num_index = int(soup.find('pl-pivot-table')['index'])
    data['params']['num_index'] = num_index
    

    is_ellipsis = soup.find('pl-pivot-table')['ellipsis'] == 'true'
    is_multicol = soup.find('pl-pivot-table')['multi-col'] == 'true'
    data['params']['multi_cols'] = is_multicol
    
    col_width = {6:'2',5:'2',4:'3',3:'3',2:'3'} # Key: number of column, Value: width to be used for bootstrap
    
    uuid = pl.get_uuid()
    if(is_multicol):
        answer_dic = {
            'uuid':uuid,
            'column1':list(),
            'column2':list(),
            'row':list()
        }
    else:
        answer_dic = {
            'uuid':uuid,
            'column':list(),
            'row':list()
        }

    if num_index == 1:
        answer_dic['index'] = list()
    elif num_index == 2:
        answer_dic['index1'] = list()
        answer_dic['index2'] = list()
    
    tag_col = soup.find('pl-column')
    if tag_col.has_attr('label'):
        LABEL_COLUMN = tag_col['label']
    html_cols = tag_col.find_all('pl-choice')
    lst_colset = list()

    if(is_multicol):
        for count ,choice in enumerate(html_cols):
            dic_cols = dict()
            cell_vals = choice.text.split(' ')
            cell_vals = list(map(lambda x: x.replace('\s',' '),cell_vals))
            
            condition1 = (is_ellipsis and (len(cell_vals) == (num_col-1))) #With ellipsis, number of columns data should be num_col-1
            condition2 = ((not is_ellipsis) and (len(cell_vals) == (num_col)))#Without ellipsis, number of columns data should be num_col
            if not(condition1 or condition2):
                print("Number of columns should be equal to attribute setting")
            
            
            dic_cols['column'] = [{'inner_html':cell_val} for cell_val in cell_vals]
            dic_cols['order_col'] = count
        
            if is_ellipsis:
                dic_cols['is_ellipsis'] = {'width':col_width[num_col]}
            else:
                dic_cols['is_ellipsis'] = False
    
            if choice['correct'] == 'true':
                if not 'place' in choice.attrs:
                    print("Place of column answer isn't specified")

                if choice['place'] == "1":
                    answer_dic['column1'].append(count)
                elif choice['place'] == "2":
                    answer_dic['column2'].append(count)
                
            lst_colset.append(dic_cols)
    else:
        for count ,choice in enumerate(html_cols):
            dic_cols = dict()
            cell_vals = choice.text.split(' ')
            cell_vals = list(map(lambda x: x.replace('\s',' '),cell_vals))
            
            condition1 = (is_ellipsis and (len(cell_vals) == (num_col-1))) #With ellipsis, number of columns data should be num_col-1
            condition2 = ((not is_ellipsis) and (len(cell_vals) == (num_col)))#Without ellipsis, number of columns data should be num_col
            if not(condition1 or condition2):
                print("Number of columns should be equal to attribute setting")
            
            
            dic_cols['column'] = [{'inner_html':cell_val} for cell_val in cell_vals]
            dic_cols['order_col'] = count
        
            if is_ellipsis:
                dic_cols['is_ellipsis'] = {'width':col_width[num_col]}
            else:
                dic_cols['is_ellipsis'] = False
    
            if choice['correct'] == 'true':
                answer_dic['column'].append(count)
                
            lst_colset.append(dic_cols)
    
    
        
    tag_indice = soup.find('pl-index')
    if tag_indice.has_attr('label'):
        LABEL_INDEX = tag_indice['label']

    html_indice = tag_indice.find_all('pl-choice')
    lst_indice_set = list()

    if num_index == 1:

        for count ,choice in enumerate(html_indice):
            dic_indice = dict()
            cell_vals = choice.text.split(' ')
            cell_vals = list(map(lambda x: x.replace('\s',' '),cell_vals))
            
            #Index needs one more text chunk than row, because it has index-label cell
            condition1 = (is_ellipsis and (len(cell_vals) == (num_row))) #With ellipsis, number of columns data should be num_col
            condition2 = ((not is_ellipsis) and (len(cell_vals) == (num_row + 1)))#Without ellipsis, number of columns data should be num_col + 1
            if not(condition1 or condition2):
                print("Number of indice should be equal to attribute setting")
            
            
            dic_indice['index'] = [{'inner_html':cell_val} for cell_val in cell_vals]
            dic_indice['order_index'] = count
            dic_indice['is_ellipsis'] = is_ellipsis
            
            
            if choice['correct'] == 'true':
                answer_dic['index'].append(count)
            
            lst_indice_set.append(dic_indice)

    elif num_index == 2:

        for count ,choice in enumerate(html_indice):
            dic_indice = dict()
            cell_vals = choice.text.split(' ')
            cell_vals = list(map(lambda x: x.replace('\s',' '),cell_vals))
            
            #Index needs one more text chunk than row, because it has index-label cell
            condition1 = (is_ellipsis and (len(cell_vals) == (num_row))) #With ellipsis, number of columns data should be num_col
            condition2 = ((not is_ellipsis) and (len(cell_vals) == (num_row + 1)))#Without ellipsis, number of columns data should be num_col + 1
            if not(condition1 or condition2):
                print("Number of indice should be equal to attribute setting")
            
            
            dic_indice['index'] = [{'inner_html':cell_val} for cell_val in cell_vals]
            dic_indice['order_index'] = count
            dic_indice['is_ellipsis'] = is_ellipsis
            
            
            if choice['correct'] == 'true':
                if not 'place' in choice.attrs:
                    print("Place of index answer isn't specified")

                if choice['place'] == "1":
                    answer_dic['index1'].append(count)
                elif choice['place'] == "2":
                    answer_dic['index2'].append(count)
            
            lst_indice_set.append(dic_indice)

    tag_row = soup.find('pl-row')
    if tag_row.has_attr('label'):
        LABEL_ROW = tag_row['label']

    html_rows = tag_row.find_all('pl-choice')
    lst_rows = list()
    for count ,choice in enumerate(html_rows):
        dic_rows = dict()
        cell_vals = choice.text.split(' ')
        cell_vals = list(map(lambda x: x.replace('\s',' '),cell_vals))
        
        condition1 = (is_ellipsis and (len(cell_vals) == (num_row-1))) #With ellipsis, number of columns data should be num_col-1
        condition2 = ((not is_ellipsis) and (len(cell_vals) == (num_row)))#Without ellipsis, number of columns data should be num_col
        if not(condition1 or condition2):
            print("Number of rows should be equal to attribute setting")
            

        dic_rows['row'] = [{'inner_html':cell_val} for cell_val in cell_vals]
        dic_rows['order_row'] = count
        dic_rows['is_ellipsis'] = is_ellipsis
        
        
        if choice['correct'] == 'true':
            #which row should be placed in which place
            place = json.loads(choice['place'])
            answer_dic['row'].append(place)
        else:
            answer_dic['row'].append(None)
        
        lst_rows.append(dic_rows)
    
    
    data['params']['df_set'] = dict()
    data['params']['df_set']['column_set'] = lst_colset
    data['params']['df_set']['column_label'] = LABEL_COLUMN if tag_col.has_attr('label') else False

    data['params']['df_set']['indice_set'] = lst_indice_set
    data['params']['df_set']['indice_label'] = LABEL_INDEX if tag_indice.has_attr('label') else False

    data['params']['df_set']['row_set'] = lst_rows
    data['params']['df_set']['row_label'] = LABEL_ROW if tag_row.has_attr('label') else False

    data['params']['df_set']['dropzone_label'] = drop_label if drop_label else False

    data['params']['df_set']['width'] = col_width[num_col]
    data['params']['df_set']['question_uuid'] = uuid
    data['correct_answers'][uuid] = answer_dic


def render(element_html, data):
    uuid = data['params']['df_set']['question_uuid']
    label_dropzone = data['params']['df_set']['dropzone_label']

    num_index = data['params']['num_index']
    label_index = data['params']['df_set']['indice_label']

    num_col = data['params']['num_col']
    num_col = [True for i in range(0,num_col)]
    label_col = data['params']['df_set']['column_label']

    width = data['params']['df_set']['width']

    num_row = data['params']['num_row']
    num_row = [True for i in range(0,num_row+1)]
    label_row = data['params']['df_set']['row_label']

    num_raw_dropzone = [{'order_zone':i} for i in range(0,len(num_col)-1)]



    if data['panel'] == 'question':
        if num_index == 1:
            
            html_params = {
                'question':True,
                'column_set':data['params']['df_set']['column_set'],
                'num_index':1,
                'indice_set':data['params']['df_set']['indice_set'],
                'is_multicol':data['params']['multi_cols'],
                'row_set':data['params']['df_set']['row_set'],
                'uuid':data['params']['df_set']['question_uuid'],
                'width':width,
                'num_col':num_col,
                'num_row':num_row,
                'num_row_dropzone':num_raw_dropzone,
                'num_row_dropzone_val':len(num_raw_dropzone),
                'answer_col_text' : label_col if label_col else DEFAULT_STRING_COLUMN,
                'answer_index_text': label_index if label_index else DEFAULT_STRING_INDEX,
                'answer_row_text': label_row if label_row else DEFAULT_STRING_ROW,
                'anwer_drop_zone': label_dropzone if label_dropzone else DEFAULT_STRING_DROP
            }

            with open('pl-pivot-table.mustache', 'r') as f:
                return chevron.render(f, html_params).strip()
                
        elif num_index == 2:
            
        
            html_params = {
                'question':True,
                'column_set':data['params']['df_set']['column_set'],
                'num_index':2,
                'indice_set_for_double':data['params']['df_set']['indice_set'],
                'is_multicol':data['params']['multi_cols'],
                'row_set':data['params']['df_set']['row_set'],
                'uuid':data['params']['df_set']['question_uuid'],
                'width':width,
                'num_col':num_col,
                'num_row_for_double':num_row,
                'calibration':"calibration",
                'num_row_dropzone':num_raw_dropzone,
                'num_row_dropzone_val':len(num_raw_dropzone),
                'answer_col_text' : label_col if label_col else DEFAULT_STRING_COLUMN,
                'answer_index_text': label_index if label_index else DEFAULT_STRING_INDEX,
                'answer_row_text': label_row if label_row else DEFAULT_STRING_ROW,
                'anwer_drop_zone': label_dropzone if label_dropzone else DEFAULT_STRING_DROP
            }

            with open('pl-pivot-table.mustache', 'r') as f:
                return chevron.render(f, html_params).strip()
    

    if data['panel'] == 'submission':
        html_params = {
            'submission':data['partial_scores'][uuid]['feedback']
        }
        with open('pl-pivot-table.mustache', 'r') as f:
            return chevron.render(f, html_params).strip()
        
    if data['panel'] == 'answer':
        html_params = {
            'answer':data['partial_scores'][uuid]['feedback']
        }
        with open('pl-pivot-table.mustache', 'r') as f:
            return chevron.render(f, html_params).strip()

        
        

def parse(element_html, data):
    is_multicol =  data['params']['multi_cols']
    
    if(is_multicol):
        uuid = data['params']['df_set']['question_uuid']
        default_return = '{"column1":null,"column2":null,"index":null,"row":null}'
        student_answer = data['raw_submitted_answers'].get(uuid+'-input',default_return)
        student_answer = json.loads(student_answer)
    
    else:
        uuid = data['params']['df_set']['question_uuid']
        default_return = '{"column":null,"index":null,"row":null}'
        student_answer = data['raw_submitted_answers'].get(uuid+'-input',default_return)
        student_answer = json.loads(student_answer)
    
    data['submitted_answers'] = student_answer

def grade(element_html, data):
    uuid = data['params']['df_set']['question_uuid']
    answer_dic = data['correct_answers'][uuid]
    num_row_dropzone = int(data['params']['num_col']) - 1
    is_multicol = data['params']['multi_cols']
    num_index = data['params']['num_index']
    final_score = 0

    if num_index == 1:
        if is_multicol:
            feedback = {'row':False,'column1':False,'column2':False,'index':False}
        else:
            feedback = {'row':False,'column':False,'index':False}
    elif num_index == 2:
        if is_multicol:
            feedback = {'row':False,'column1':False,'column2':False,'index1':False,'index2':False}
        else:
            feedback = {'row':False,'column':False,'index1':False,'index2':False}

    if num_index == 1:
        index_submitted = data['submitted_answers']['index']
        index_submitted = int(index_submitted) if type(index_submitted) == str else None
        if index_submitted in answer_dic['index']:
            final_score += 0.3
        else:
            feedback['index'] = True

    elif num_index == 2:
        index_submitted1 = data['submitted_answers']['index1']
        index_submitted2 = data['submitted_answers']['index2']

        index_submitted1 = int(index_submitted1) if type(index_submitted1) == str else None
        index_submitted2 = int(index_submitted2) if type(index_submitted2) == str else None

        if index_submitted1 in answer_dic['index1']:
            final_score += 0.15
            feedback['index1'] = True

        if index_submitted2 in answer_dic['index2']:
            final_score += 0.15
            feedback['index2'] = True
        
    
    if(is_multicol):
        col_submitted1 = data['submitted_answers']['column1']
        col_submitted2 = data['submitted_answers']['column2']

        col_submitted1 = int(col_submitted1) if type(col_submitted1) == str else None
        col_submitted2 = int(col_submitted2) if type(col_submitted2) == str else None


        if col_submitted1 in answer_dic['column1']:
            final_score += 0.15
        else:
            feedback['column1'] = True

        if col_submitted2 in answer_dic['column2']:
            final_score += 0.15
        else:
            feedback['column2'] = True

    else:
        col_submitted = data['submitted_answers']['column']
        col_submitted = int(col_submitted) if type(col_submitted) == str else None
        if col_submitted in answer_dic['column']:
            final_score += 0.3
        else:
            feedback['column'] = True
    
    row_submitted = data['submitted_answers']['rows']
    row_submitted = list(map(lambda x: int(x) if type(x) == str else None ,row_submitted))


    correct_count = 0 #This will be counted upto the number of row dropzone(Are all row choices in dropzone correct?)
    for dropzone_spot, row_choice in enumerate(row_submitted):
        if row_choice == None or correct_count == num_row_dropzone:
            break
        
        
        answer_row = answer_dic['row'][row_choice] #List or place of valid answer spots where row_choice should be

        if type(answer_row) == list:
            answer_row = list(map(lambda x: x-1, answer_row)) #Subtract each element by one => the attribute input starting from one: place="[1,2,3]"
            if dropzone_spot in answer_row:
                correct_count += 1
        else:
            if answer_row == None:
                continue
            answer_row -= 1
            if dropzone_spot == answer_row:
                correct_count += 1


    if correct_count == num_row_dropzone:
        final_score += 0.4
    else:
        feedback['row'] = True


    data['partial_scores'][uuid] = {'score':final_score,
                                    'feedback':feedback,
                                    'weight':1}
