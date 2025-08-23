import random, math
import pandas as pd
import numpy as np
import prairielearn as pl
# import datascience
# from datascience import Table


### To author, only edit this portion ###
authoring = False #TYPE: BOOL. change to True!

# For the columns you want to be included in the question:
change_columns = False #TYPE: BOOL. Change to True if you wish to use your own columns instead of random selection.

#   One has to be the categorical column (cat)
#cv options = ['Sugar', 'Albumin', 'Blood Pressure', 'Age', 'Bacteria', 'Hypertension', 'Coronary Artery Disease', 'Pedal Edema', 'Anemia']
categorical = '' #TYPE: STRING, must use quotations

#   One has to be the numerical column (nv)
#nv options = ['Specific Gravity', 'Blood Glucose Random', 'Blood Urea', 'Serum Creatinine', 'Sodium', 'Potassium', 'Hemoglobin', 'Packed Cell Volume', 'White Blood Cell Count', 'Red Blood Cell Count']
numerical = '' #TYPE: STRING, must use quotations

# For the first .group function:
group_by = 'average' #TYPE: STRING. Change to: "average", "max", OR "min". MUST have single quotations!

# For the second function
function = 'sort' # TYPE: STRING. change to "sort", "select", OR "where". MUST have single quotations!

# For sort (leave as is if not applicable):
descending_true = False #TYPE: BOOL. change to True (descending) or False (ascending)

# For where (leave as is if not applicable):
are_above = False #TYPE: BOOL. change to True (are.above) or False (are.below)

# For select (leave as is if not applicable):
column = None #TYPE: STRING. change to the column you want selected as part of the .select call.

### End portion ###

def generate(data):
    
    def question_generator():
        df = pd.read_csv('https://www.inferentialthinking.com/data/ckd.csv')
        cv = ['Sugar', 'Albumin', 'Blood Pressure', 'Age', 'Bacteria', 'Hypertension', 'Coronary Artery Disease', 'Pedal Edema', 'Anemia']
        nv = ['Specific Gravity', 'Blood Glucose Random', 'Blood Urea', 'Serum Creatinine', 'Sodium', 'Potassium', 'Hemoglobin', 'Packed Cell Volume', 'White Blood Cell Count', 'Red Blood Cell Count']
        cat = cv[random.randrange(len(cv))]
        num = nv[random.randrange(len(nv))]
        q = random.randrange(3)
        index = random.randrange(3)
        collect = ['average', 'max', 'min'][index]
        func = ['np.average', 'max', 'min'][index]
        pd_func = ['mean', 'max', 'min'][index]
        number = 0 
        if q == 0: #.where
            value = round(np.mean(list(df.groupby(cat)[num].agg(pd_func))), 3)
            i = random.randrange(2)
            where_arg = ['are.above', 'are.below'][i]
            flip = ['above', 'below'][i]
            number = value
            question = f"create a table containing only the values where the {collect} of {num} for each unique {cat} value is {flip} {value}."
            answer = f"health.group('{cat}', {func}).where('{num} {collect}', {where_arg}({value}))"
        elif q == 1: #.sort
            i = random.randrange(2)
            flip = ['ascending', 'descending'][i]
            boolean = ['False', 'True'][i]
            question = f"create a table that is sorted in {flip} order by the {collect} of {num} for each unique {cat} value."
            answer = f"health.group('{cat}', {func}).sort('{num} {collect}', descending={boolean})"
        elif q == 2: #.select
            col = nv[random.randrange(len(nv))]
            question = f"create a 2 column table containing {cat} and {col} {collect} respectively for each unique {cat} value."
            answer = f"health.group('{cat}', {func}).select('{cat}', '{col} {collect}')"
        return [question, answer, 'https://www.inferentialthinking.com/data/ckd.csv', 'health', number]

    def authoring_question():
        df = pd.read_csv('https://www.inferentialthinking.com/data/ckd.csv')
        
        if not change_columns: #columns are randomly selected
            cv = ['Sugar', 'Albumin', 'Blood Pressure', 'Age', 'Bacteria', 'Hypertension', 'Coronary Artery Disease', 'Pedal Edema', 'Anemia']
            nv = ['Specific Gravity', 'Blood Glucose Random', 'Blood Urea', 'Serum Creatinine', 'Sodium', 'Potassium', 'Hemoglobin', 'Packed Cell Volume', 'White Blood Cell Count', 'Red Blood Cell Count']
            cat = cv[random.randrange(len(cv))]
            num = nv[random.randrange(len(nv))]
        else:
            cat = categorical
            num = numerical
            
        number = 0
        collect = group_by.lower()
        pd_func = group_by.lower()
        func = group_by.lower()
        
        if pd_func == 'average': #change to correct word
            pd_func = 'mean'
        if func == 'average': #change to correct word
            func = 'np.average'
        
        if function.lower() == 'where':
            value = round(np.mean(list(df.groupby(cat)[num].agg(pd_func))), 3)
            flip = 'above'
            where_arg = 'are.above'
            if not are_above: #are_above:
                flip = 'below'
                where_arg = 'are.below'
            number = value
            question = f"create a table containing only the values where the {collect} of {num} for each unique {cat} value is {flip} {value}."
            answer = f"health.group('{cat}', {func}).where('{num} {collect}', {where_arg}({value}))"
            
        elif function.lower() == 'sort':
            flip = 'descending'
            boolean = 'True'
            if not descending_true: #desc = false
                flip = 'ascending'
                boolean = 'False'
            question = f"create a table that is sorted in {flip} order by the {collect} of {num} for each unique {cat} value."
            answer = f"health.group('{cat}', {func}).sort('{num} {collect}', descending={boolean})"
            
        elif function.lower() == 'select':
            if not column:
                col = nv[random.randrange(len(nv))]
            else:
                col = column
            question = f"create a 2 column table containing {cat} and {col} {collect} respectively for each unique {cat} value."
            answer = f"health.group('{cat}', {func}).select('{cat}', '{col} {collect}')"
            
        return [question, answer, 'https://www.inferentialthinking.com/data/ckd.csv', 'health', number]


    if not authoring: #this is the implemented pseudorandom question generator.
        q_a = question_generator()
        question = q_a[0]
        answer = q_a[1]
        a = random.randint(100, 200)
        ans = "{0:b}".format(a)
        data["params"]["a"] = a
        data["params"]["question"] = question
        data["correct_answers"]["b"] = answer
        df = pd.read_csv(q_a[2]).head(5)
        data['params']['df'] = pl.to_json(df)
        data["params"]["tbl_name"] = q_a[3]
        data["params"]["number"] = q_a[4]
        return data
    
    elif authoring:
        q_a = authoring_question()
        question = q_a[0]
        answer = q_a[1]
        a = random.randint(100, 200)
        ans = "{0:b}".format(a)
        data["params"]["a"] = a
        data["params"]["question"] = question
        data["correct_answers"]["b"] = answer
        df = pd.read_csv(q_a[2]).head(5)
        data['params']['df'] = pl.to_json(df)
        data["params"]["tbl_name"] = q_a[3]
        data["params"]["number"] = q_a[4]
        return data
        

"""
# import random, math
# import pandas as pd
# import numpy as np
# import prairielearn as pl
# #import datascience
# #from datascience import Table

# def generate(data):
    
#     def question_generator():
#         df = pd.read_csv('https://www.inferentialthinking.com/data/ckd.csv')
#         cv = ['Sugar', 'Albumin', 'Blood Pressure', 'Age', 'Bacteria', 'Hypertension', 'Coronary Artery Disease', 'Pedal Edema', 'Anemia']
#         nv = ['Specific Gravity', 'Blood Glucose Random', 'Blood Urea', 'Serum Creatinine', 'Sodium', 'Potassium', 'Hemoglobin', 'Packed Cell Volume', 'White Blood Cell Count', 'Red Blood Cell Count']
#         cat = cv[random.randrange(len(cv))]
#         num = nv[random.randrange(len(nv))]
#         q = random.randrange(3)
#         index = random.randrange(3)
#         collect = ['average', 'max', 'min'][index]
#         func = ['np.average', 'max', 'min'][index]
#         pd_func = ['mean', 'max', 'min'][index]
#         number = 0
#         if q == 0: #.where
#             value = round(np.mean(list(df.groupby(cat)[num].agg(pd_func))), 3)
#             i = random.randrange(2)
#             where_arg = ['are.above', 'are.below'][i]
#             flip = ['above', 'below'][i]
#             number = value
#             question = f"create a table containing only the values where the {collect} of {num} for each unique {cat} value is {flip} {value}."
#             answer = f"health.group('{cat}', {func}).where('{num} {collect}', {where_arg}({value}))"
#         elif q == 1: #.sort
#             i = random.randrange(2)
#             flip = ['ascending', 'descending'][i]
#             boolean = ['False', 'True'][i]
#             question = f"create a table that is sorted in {flip} order by the {collect} of {num} for each unique {cat} value."
#             answer = f"health.group('{cat}', {func}).sort('{num} {collect}', descending={boolean})"
#         elif q == 2: #.select
#             col = nv[random.randrange(len(nv))]
#             question = f"create a 2 column table containing {cat} and {col} {collect} respectively for each unique {cat} value."
#             answer = f"health.group('{cat}', {func}).select('{cat}', '{col} {collect}')"
#         return [question, answer, 'https://www.inferentialthinking.com/data/ckd.csv', 'health', number]

#     q_a = question_generator()
#     question = q_a[0]
#     answer = q_a[1]
#     a = random.randint(100, 200)
#     ans = "{0:b}".format(a)
#     data["params"]["a"] = a
#     data["params"]["question"] = question
#     data["correct_answers"]["b"] = answer
#     df = pd.read_csv(q_a[2]).head(5)
#     data['params']['df'] = pl.to_json(df)
#     data["params"]["tbl_name"] = q_a[3]
#     data["params"]["number"] = q_a[4]
#     return data
"""