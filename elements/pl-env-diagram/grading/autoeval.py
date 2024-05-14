import inspect
import heapq
try:
    import autoeval_frame as frame
except:
    import grading.autoeval_frame as frame
import os, contextlib
import re

# i refer to this as "framenode" in some places. this is to avoid ambiguity. 
Frame = frame.Frame

class FrameTree():

    def __init__(self, codestring):
        # The "root" (aka Global) frame of the tree. Points to a Frame object.
        self.root = None
        # The amount of frames in our tree thusfar.
        self.framecounter = 0
        # Associates a frame object to a frame node (or in the case of Global, at least for the time being, "Global" to a frame node.) This is used to identify the parent frame of the frame being added.
        self.fobj_framenode_dict = {}
        # Associates id(function.__code__) to a list of frames that use it. This is used so that we can assign parents to frames.
        self.codestrID_frame_dict = {}
        # Associates id(function.__code__) to a parent frame. This is used so that we can identify the parent of each function for grading.
        self.codestrID_parent_dict = {}
        # Make sure the inputted code actually runs before generating the FrameTree
        try:
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stdout(devnull):
                    exec(codestring, {})
        except:
            raise Exception("Inputted codestring errs.")
        # Generate the FrameTree! 
        codestring = self.initialize_Frames(codestring)
        exitlines_pq, exitlines_to_fobj_dict = self.get_exitlines()
        self.get_bindings(codestring, exitlines_pq, exitlines_to_fobj_dict)
    
    def add_newFrame(self): 
        """ Adds a new Frame to the FrameTree. 
        """
        # Get the frame object of the frame being added. The current frame we are in is add_newFrame. We want the frame that called it.
        fobj = inspect.currentframe().f_back
        # If no Frames have been initialized yet, set the frame as the Global frame and the root
        if self.framecounter == 0:
            name = "Global"
            frame = Frame(name = name, fobj = fobj, index="Global")
            self.fobj_framenode_dict[fobj] = frame
            self.root = frame
        # If this frame is not the Global frame, initialize as normal.
        else: 
            # The name of the Frame is the name of the function that it is calling. 
            name = fobj.f_code.co_name
            # Create the Frame with all of this information. Name it however many frames there are. 
            frame = Frame(name = name, fobj=fobj, index=str(self.framecounter))
            # Add the new Frame to the frame object <--> Frame dict so children of this Frame are able to find it. 
            self.fobj_framenode_dict[fobj] = frame
        # Add your own code object to the dictionary
        if id(fobj.f_code) in self.codestrID_frame_dict:
            self.codestrID_frame_dict[id(fobj.f_code)].append(frame)
        else:
            self.codestrID_frame_dict[id(fobj.f_code)] = [frame]
        # Increment the amount of Frames. 
        self.framecounter += 1
        return frame
    
    
    def initialize_Frames(self, codestring):
        """This function adds a new line of code initializing the FrameNode in each function definition. 
        It then runs the modified code. We can later use all of the created FrameNodes to identify where to put
        listeners that will give us more information.
        
        I accomplish this by locating 'def' statements in the code and then initializing a new Frame in the line after.
        Then the code gets run in exec."""

        # Create a list of lines of code.
        code_list = codestring.split("\n")
        # Deletes whitespace at the beginning of code
        while len(code_list) > 0 and re.fullmatch("\s*", code_list[0]):
            del code_list[0]

        # Insert the line that will create the Global Frame.
        code_list.insert(0, "self.add_newFrame()")
        # Insert lines that will create all non-Global Frames by identifying ####
        i = 1 # TODO: modify to consider initalized vars // I am no longer sure what this means
        ### i = 1
        # Keep track of how much the current line has been shifted by (for example, if I am on what was line 2 but I added 3 lines before it, the shift is 3)
        shift = 0
        while i < len(code_list):     
            if code_list[i].lstrip(' ')[:4] == "def ":
                def_line = i
                # find the indent size after the def
                whitespace = 0
                # The amount of whitespace indented after a def statement must be greater than 0, so we can continue while the whitespace is 0.
                while whitespace == 0:
                    i = i + 1
                    # check to make sure it's not just an empty line
                    if len(code_list[i].split()) > 0:
                        # get size of whitespace before code
                        whitespace = len(code_list[i]) - len(code_list[i].lstrip(' '))
                        # set this back to the previous line just in case the first non-empty line is a def statement.
                        i = i - 1
                # insert the code to create the FrameNode
                # TODO: make sure none of the variables are already in scope in the code.
                code_list.insert(def_line + 1, ' '*whitespace + "self.add_newFrame()") 
                shift += 1

            i = i + 1
        codestring = str.join("\n", code_list)
        d =  {"self":self, "inspect":inspect}
        try:
            # These two 'with' statements silence the execution so no print statements are printed, which can bug out prarielearn. 
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stdout(devnull):
                    exec(codestring, d)
        except:
            raise Exception("Error evaluating the autogenerated code. Please contact an administrator.")    
        return codestring
    
    def get_exitlines(self):
        """Returns a max heap of exit lines, and a dictionary mapping exit lines to Frame objects."""

        exitlines_pq = []
        exitlines_to_fobj_dict = {} # might be able to replace this with an exitlines_pq to var list mapping. if so, change description of this func. 
        for fobj in self.fobj_framenode_dict:
            frame = self.fobj_framenode_dict[fobj]
            if fobj == "Global":
                fobj = frame.fobj
            exitline = frame.fobj.f_lineno - 1
            exitlines_pq.append(exitline)
            exitlines_to_fobj_dict[exitline] = fobj

        # remove duplicate exit lines
        exitlines_pq = list(set(exitlines_pq))
        # heapify the list
        heapq._heapify_max(exitlines_pq)
        return exitlines_pq, exitlines_to_fobj_dict
    
    def get_bindings(self, codestring, exitlines_pq, exitlines_to_fobj_dict):
        """Inserts trackers into the codestring just before exitlines that add bindings to Frames. Deletes all previous Frames in FrameTree before doing this."""

        # clear the dictionaries, frame counter, and Frames.
        self.fobj_framenode_dict = {}
        self.framecounter = 0
        self.root = None

        # 
        #exitlines_pq = exitlines_pq.copy()
        code_list = codestring.split("\n")

        # TODO: fix to include correct variable names
        # set variable names for things we are using to store tracking info. (TODO: CHNAGE NAME GLOBVAR)
        trk_var_names_dict = {"self":"self", "frame":"frame","return":"returnval", "locals":"locs", "globvar":"globvar", "bindings":"bindings", "fobj_framenode_dict":"fobj_framenode_dict"}
        # handle the Global frame
        exitline = heapq._heappop_max(exitlines_pq)
        code_list.insert(exitline + 1, trk_var_names_dict["globvar"] + '=' "locals()")
        # TODO: 'var' might also be an issue here..     
        # TODO: var names
        code_list.insert(exitline + 2, trk_var_names_dict["frame"] + '=' "self.fobj_framenode_dict[inspect.currentframe()]")
        code_list.insert(exitline + 3, trk_var_names_dict["frame"] + ".bind(" + trk_var_names_dict["globvar"] + "," + "exclude =  ['" + trk_var_names_dict["frame"] + "', 'self', 'inspect', '__builtins__'" "]" + "," + "codestrID_frame_dict = self.codestrID_frame_dict" + "," + "codestrID_parent_dict =  self.codestrID_parent_dict" + ")") 

        # get largest exitline
        while len(exitlines_pq) > 0:
            # get the current exitline (also the first line we insert into)!
            exitline = heapq._heappop_max(exitlines_pq)
            i = exitline
            whitespace = len(code_list[i]) - len(code_list[i].lstrip(' '))
            if code_list[i].lstrip(' ')[:7] == "return ":
                returnval = code_list[i].lstrip(' ')[7:]
                # set name for returnval in the code
                # change the return line to return the stored value
                code_list[i] = ' '*whitespace + "return " + trk_var_names_dict["return"]
                # insert a line that records the return value
                code_list.insert(i, ' '*whitespace + trk_var_names_dict["return"] + '=' + returnval)
            # store local variables at this point
            code_list.insert(i + 1, ' '*whitespace + trk_var_names_dict["locals"] + '=' "locals()")
            # store bindings at this point
            # TODO: 'var' might also be an issue here..
            code_list.insert(i + 2, ' '*whitespace + trk_var_names_dict["bindings"] + '=' + trk_var_names_dict["locals"])
            code_list.insert(i + 3, ' '*whitespace + trk_var_names_dict["frame"] + '=' "self.fobj_framenode_dict[inspect.currentframe()]")
            # TODO: var names
            code_list.insert(i + 4, ' '*whitespace + trk_var_names_dict["frame"] + ".bind(" + trk_var_names_dict["bindings"] + "," + "codestrID_frame_dict = self.codestrID_frame_dict" + "," + "codestrID_parent_dict =  self.codestrID_parent_dict" +")")

        # get modified code with Frame initialization
        newcode = str.join("\n", code_list)
        d =  {"self":self, "inspect":inspect}
        # then execute the code
        try:
            # These two 'with' statements silence the execution so no print statements are printed, which can bug out prarielearn. 
            # TODO: REMOVE
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stdout(devnull):
                    exec(newcode, d, d)
        except:
            raise Exception("Error evaluating the autogenerated code. Please contact an administrator.")    
        # TODO: Needed?
        del self.root.bindings["globvar"]
    
    def generate_html_json(self):
        """Generates JSON corresponding to a frame. Data used for visualization is not included. """
        # stores values of objects.
        self.heap_dict = {"func":[], "list":[], "tuple":[]}
        # keeps track of how many of the same frame name exist
        self.frames_list = []
        # maps id() of objects to their index in heapdict. 
        mem_to_index_dict = {}
        def handle_variable(raw_variable, name = None, listIndex = None, varIndex = None):
            # TODO: i dont know whether its better to have these as separate lines for readibility, or in just one line
                variable = {
                    "val": None,
                    "name": name, # none if list element
                    "varIndex": varIndex, # none if list element
                }
                # TODO: i dont know whether its better to have the primitives as separate lines for readibility, or in just one line
                if type(raw_variable).__name__ == "str":
                    variable["val"] = raw_variable.__repr__()
                elif type(raw_variable).__name__ == "int":
                    variable["val"] = raw_variable.__repr__()
                elif type(raw_variable).__name__ == "float":
                    variable["val"] = raw_variable.__repr__()
                elif type(raw_variable).__name__ == "boolean":
                    variable["val"] = raw_variable.__repr__()
                elif type(raw_variable).__name__ == "function":
                    if id(raw_variable) in mem_to_index_dict:
                        func_index = mem_to_index_dict[id(raw_variable)]  
                        variable["val"] = "#heap-func-" + str(func_index)  
                    else:
                        variable["val"] = "#heap-func-" + str(len(self.heap_dict["func"]))
                        # Parent of the function is found by indexing the __code__ attribute into this dictionary
                        parent = self.codestrID_parent_dict[id(raw_variable.__code__)]
                        parent = parent if (parent == "Global" or not parent) else parent
                        mem_to_index_dict[id(raw_variable)] = len(self.heap_dict["func"])
                        self.heap_dict["func"].append({"name":raw_variable.__name__, 
                                                    "parent":parent, 
                                                    "funcIndex":len(self.heap_dict["func"]), 
                                                })

                elif type(raw_variable).__name__ == "list" or type(raw_variable).__name__ == "tuple":
                    seq_type_name = type(raw_variable).__name__
                    pl_key_prefix = "#heap-" + seq_type_name + "-"
                    if id(raw_variable) in mem_to_index_dict:
                        seq_index = mem_to_index_dict[id(raw_variable)]  
                        variable["val"] = pl_key_prefix + str(seq_index)  
                    else:
                        variable["val"] = pl_key_prefix + str(len(self.heap_dict[seq_type_name]))
                        seq = {"item":[], seq_type_name + "Index":len(self.heap_dict[seq_type_name])}
                        mem_to_index_dict[id(raw_variable)] = len(self.heap_dict[seq_type_name])
                        for i in range(len(raw_variable)):
                            seq["item"].append(handle_variable(raw_variable[i], listIndex=i))
                        self.heap_dict[seq_type_name].append(seq)

                if listIndex is not None:
                    variable["itemIndex"] = listIndex
                    del variable["name"]
                    del variable["varIndex"]

                return variable

        def addFrameToJson(frame):
            newframe = {}
            newframe["var"] = []
            if frame.__name__ != "Global":
                newframe["name"] = frame.__name__
                parent = str(frame.parent.index)
                newframe["parent"] = parent if (parent == "Global" or not parent) else "f" + parent
                # keep this line?
                newframe["return"] = None
                # may cause formatting issues, check this
            newframe["frameIndex"] = str(len(self.frames_list))
            self.frames_list.append(newframe)

            i = 0
            for varname in frame.bindings:
                if varname == "returnval":
                    variable = handle_variable(frame.bindings[varname], name = varname, varIndex=i)
                    newframe["return"] = {"val":variable["val"]}
                # TODO: MOVE TO FRAMETREE DEF
                else:
                    newframe["var"].append(handle_variable(frame.bindings[varname], name = varname, varIndex=i))
                i = i + 1
            for child in frame.children:
                addFrameToJson(child)
        addFrameToJson(self.root)
        return {"heap": self.heap_dict, "frame":self.frames_list}

    def __str__(self):
        line_list = []
        framepq = [self.root]
        while len(framepq) > 0:
            line_list.append(framepq[0].__name__)
            for key in framepq[0].bindings:
                line_list.append("    " + key + " = " + str(type(framepq[0].bindings[key])))
            for child in framepq[0].children:
                framepq.append(child)
            framepq = framepq[1:]
        return "\n".join(line_list)