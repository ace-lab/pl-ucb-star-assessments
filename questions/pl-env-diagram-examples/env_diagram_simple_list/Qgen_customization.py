import question_gen

######################################################################
######################### CUSTOM FUNCTIONS ###########################
######################################################################

# Here you can write your own functions for name/value/line generation. You cannot provide functions that take in a variable.

######################################################################
###################### REPLACEMENT OPTIONS ###########################
######################################################################

# Below there are options for replacement of various parts of your default code. 
# Please note that replacement occurs in the following order:
# 1. Value replacements
# 2. Special replacements
# 3. Namespace replacements (replace the names of variables/functions)

# WARNING: it is possible to choose options that do not work and will not compile. 
# Please test any given problem a few times (not just generating the problem, but 
# also completing it) before releasing it to students.

######################################################################
################## OPTIONS FOR NAMESPACE REPLACEMENT #################
######################################################################

# Provide possible options to rename variables and functions with. You should provide all function/variable names here, even if you would like to leave them unchanged. The code will not necessarily err if you neglect to do this, but in some cases or on some seeds it might. This is because the question generation stage cannot detect all of the variables in the codestring unless you provide them, so it won't know if there are overlapping names.
# WARNING: If you do not provide enough options such that each variable can get a unique name, the question generator will time out. 
# WARNING 2: If you provide options for some variables but not for others, and it is possible for other variables to be given the same name as the unchanged variable(s),
# the code may err or you may just be testing students on a different kind of environment diagram in some cases. If you would like to leave a variable unchanged, just 
# provide the variable name and only itself as an option in the list, and it should go before randomizable variable names. For example, if you wanted to leave "f" unchanged, provide "f":["f"], and it should go first.

allowed_names = {
    # below are our variable names
    "a": [question_gen.lowercase_letters], 
    "b": [question_gen.lowercase_letters],
    "c": [question_gen.lowercase_letters],
    "f": [question_gen.common_function_names], 
    }

######################################################################
############# OPTIONS FOR VALUE ASSIGNMENT REPLACEMENT ###############
######################################################################

# On lines where a variable assignment happens, you can provide different options for the value
# assigned. Indicate the line number, and the value options. Line numbers that correspond to 
# no variable assignment will be ignored. Variable assignments with no line number given will be
# left alone. 

# NOTE: question_gen.py counts the first line that isn't just whitespace as line 0. Comments count. Keep this in mind when indexing lines.

# NOTE: You must provide either functions that can be evaluated to create a value that is a string, a list of strings, or a string containing the value you want.
    # For example, if you wanted the value on line 3 to be the integer 5000, you would have to provide that as '5000'. See line 3 below. 
    # If you wanted the value on line 1 to be "Cats say meow", you would have to provide that as '"Cats say meow"' with additional outside quotations. See line 1 below.
    # If you want the new value to include the name of a variable, use the name in the default code. See the example in line 3 below. 

allowed_assignment_values = {
    0:[question_gen.small_int],
    1:['"bok"', '"cvijet"', '"morski pas"', '"dan garcia"', '"armando fox"', '"narges norouzi"'],
    4:["f(b)", "f(a)", "f(9)", "f('plavu')"],
    }

######################################################################
##################### SPECIAL REPLACEMENT OPTIONS ####################
######################################################################

# If you would instead like to replace particular tags in your code with a set of options, you can use this dictionary. 
    # Tags should not appear in any way outside of the intended tags as these will use simple pythonic string substitution. We recommend naming your tags
    # with a sequence of characters that are unlikely to appear in normal code, like $5$.
    # This might be useful for segments of the code that you may want to replace that are not covered by variable name substitution or value assignment changes. 
    # For example, you could make it so that some randomized code includes a .extend statement while other includes a .append statement. 
    # Rules for formatting everything as strings applies. Read the comments on the above dictionary for explanation. 
# WARNING: If you use this feature, please try a few randomizations on your own to make sure it looks and grades how you expect it to. Small mistakes can cause the problem to not work as expected.

special_replacements = {
}

######################################################################
########################## INPUT BASE CODE ###########################
######################################################################

# You can choose to input the problem's base code as a string,

code_string = """ 
a = 5
b = "hello"
def f(c):
    return [a, b, c]
c = f(b)
""" 

# Or as a filepath (from question_gen.py). If you do both, the generator will prioritize the string. 

code_filepath = None

######################################################################
############################## TIMEOUT ###############################
######################################################################

timeout = None

######################################################################
############################ GENERATION ##############################
######################################################################

# DO NOT MODIFY THE BELOW LINE

generateQ = lambda seed : question_gen.generate_question(allowed_names, allowed_assignment_values, special_replacements, code_string, code_filepath, seed)

# These lines show you a potential result of your problem. We recommend running this file a few times to see if it works how you expect before testing it on Prarielearn.  
# COMMENT OUT THESE LINES WHEN TESTING PRARIELEARN OR IT WILL CAUSE ERRORS

#import random
#result_code_string = generateQ(seed = random.randint(0, 50))
#print(result_code_string)

