###############################################
#          This code is in-progress           #
# It's designed for randomized questions      #
###############################################
#   Two parts needed to be done
#   1. Formatting for mustache
#   2. Grading
#   
#   Implemented done 
#   1. Random values generating for each cell
#

from typing import cast
import chevron
import lxml.html
import json
import pandas as pd
import prairielearn as pl
from bs4 import BeautifulSoup
import numpy as np

def prepare(element_html, data):
    soup = BeautifulSoup(element_html)
    
    num_col = int(soup.find('pl-pivot-table')['col'])
    if num_col < 2:
        print("Invalid column number")
    data['params']['num_col'] = num_col
    
    num_row = int(soup.find('pl-pivot-table')['row'])
    if num_row < 1:
        print("Invalid row number")
    data['params']['num_row'] = num_row
    
    num_index = int(soup.find('pl-pivot-table')['index'])
    data['params']['num_index'] = num_index
    
    is_multicol = soup.find('pl-pivot-table')['multi-col'] == 'true'
    data['params']['multi_cols'] = is_multicol
    
    col_width = {6:'2',5:'2',4:'3',3:'3',2:'3'}
    
    uuid = pl.get_uuid()
    
    possible_columns = ['foo', 'bar', 'baz', 'qux', 'corge', 'grault', 'garply']
    possible_cat_values = ['A','B','C','D','E','F','G']
    possible_num_values = np.arange(1,11)
    possible_agg_funcs = ['sum','mean','count','min','max']
    
    # Create a pandas dataframe. The columns are the possible columns selected without replacement, and the rows are the possible values. At least two columns must be categorical and one must be numerical. Keep track of which columns are categorical and which are numerical.
    
    columns = np.random.choice(possible_columns, size=num_col, replace=False)
    
    # pick two columns to be categorical
    cat_cols = np.random.choice(columns, size=2, replace=False)
    num_cols = [col for col in columns if col not in cat_cols]
    
    df = pd.DataFrame(columns=columns)
    for cat_col in cat_cols:
        df[cat_col] = np.random.choice(possible_cat_values, size=num_row, replace=True)
    for num_col in num_cols:
        df[num_col] = np.random.choice(possible_num_values, size=num_row, replace=True)
        
    col_pivot, index_pivot = np.random.choice(columns, size=2, replace=False)
    val_pivot = np.random.choice(columns, size=1, replace=False)
    agg_func  = np.random.choice(possible_agg_funcs)
    
    # Create a pivot table with the selected columns and aggregation function. The index is the other column.
    df_pivot = pd.pivot_table(df, index=index_pivot, columns=col_pivot, values=val_pivot, aggfunc=agg_func)
    df_pivot_str = f"df_pivot = pd.pivot_table(df, index={index_pivot}, columns={col_pivot}, values={val_pivot}, aggfunc={agg_func})"
        
    
        
    data['params']['df_set'] = dict()
    data['params']['df_set']['column_set'] = {
        'column': df_pivot.columns.tolist(),
        'order_col': 0,
        'is_ellipsis': False
                                              }
    data['params']['df_set']['indice_set'] = {
        'index': [{'inner_html':cell_val} for cell_val in df_pivot.index.tolist()],
        'order_index': 0,
        'is_ellipsis': False
                                              }
    data['params']['df_set']['row_set'] = [
        {
            'row': [{'inner_html':cell_val} for cell_val in cell_vals],
            'order_row': count,
            'is_ellipsis': False
        }
        for count, cell_vals in enumerate(df_pivot.values.tolist())
    ]
    data['params']['df_set']['width'] = col_width[num_col]
    data['params']['df_set']['question_uuid'] = uuid
    data['correct_answers'][uuid] = df_pivot.to_json()
    # TODO FIX CORRECT ANSWERS


def render(element_html, data):
    uuid = data['params']['df_set']['question_uuid']
    num_index = data['params']['num_index']
    num_col = data['params']['num_col']
    num_col = [True for i in range(0,num_col)]
    width = data['params']['df_set']['width']

    num_row = data['params']['num_row']
    num_row = [True for i in range(0,num_row+1)]

    num_raw_dropzone = [{'order_zone':i} for i in range(0,len(num_col)-1)]
 
    if data['panel'] == 'question': # TODO EDIT mustache format
        if num_index == 1:
        
            html_params = {
                'question':True,
                'column_set':data['params']['df_set']['column_set'],
                'indice_set':data['params']['df_set']['indice_set'],
                'is_multicol':data['params']['multi_cols'],
                'row_set':data['params']['df_set']['row_set'],
                'uuid':data['params']['df_set']['question_uuid'],
                'width':width,
                'num_col':num_col,
                'num_row':num_row,
                'num_row_dropzone':num_raw_dropzone,
                'num_row_dropzone_val':len(num_raw_dropzone),
                "answer_row_text": "Choose answer row from this bank here",
                "answer_col_text": "Choose answer column from this bank here",
                "answer_index_text": "Choose answer index from this bank here",
                "answer_drop_text": "Drop selected answers here"
            }

            with open('pl-pivot-table.mustache', 'r') as f:
                return chevron.render(f, html_params).strip()
                
        elif num_index == 2:
            
        
            html_params = {
                'question':True,
                'column_set':data['params']['df_set']['column_set'],
                'indice_set':data['params']['df_set']['indice_set'],
                'is_multicol':data['params']['multi_cols'],
                'row_set':data['params']['df_set']['row_set'],
                'uuid':data['params']['df_set']['question_uuid'],
                'width':width,
                'num_col':num_col,
                'num_row':num_row,
                'calibration':return_text,
                'num_row_dropzone':num_raw_dropzone,
                'num_row_dropzone_val':len(num_raw_dropzone),
                "answer_row_text": "Choose answer row from this bank here",
                "answer_col_text": "Choose answer column from this bank here",
                "answer_index_text": "Choose answer index from this bank here",
                "answer_drop_text": "Drop selected answers here"
            }

            with open('pl-pivot-table.mustache', 'r') as f:
                return chevron.render(f, html_params).strip()
    
    if data['panel'] == 'submission':
        if num_index == 1:
            html_params = {
                'submission':data['partial_scores'][uuid]['feedback']
            }
            with open('pl-pivot-table-single.mustache', 'r') as f:
                return chevron.render(f, html_params).strip()
    
        elif num_index == 2:
            html_params = {
                'submission':data['partial_scores'][uuid]['feedback']
            }
            with open('pl-pivot-table-double.mustache', 'r') as f:
                return chevron.render(f, html_params).strip()
    

    if data['panel'] == 'answer':
        html_params = {
            'submission':data['partial_scores'][uuid]['feedback']
        }
        with open('pl-pivot-table-single.mustache', 'r') as f:
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

def grade(element_html, data): #Grade function isn't needed to be fixed. The point is storing answer data in structured way
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
