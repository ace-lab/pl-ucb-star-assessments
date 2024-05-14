class Frame():
    is_global = False

    def __init__(self, name = None, bindings=None, parent=None, children=None, fobj=None, index = None, codeloc = None):
        self.parent = parent 
        self.children = children if children else set()
        if bindings is None:
            self.bindings = {}
        self.__name__ = name
        # self's frame object
        self.fobj = fobj
        # keeps track of the memory location of the .__code__ of the function that created this frame. This is used to later identify the parent of that function as an object.
        self.codeloc = codeloc
        self.index = index

    def bind(self, name, value):
        self.bindings[name] = value  
    
    def bind(self, name_value_dict, exclude = None, codestrID_frame_dict = None, codestrID_parent_dict = None):
        if not exclude is None:
            for name in exclude:
                if name in name_value_dict:
                    del name_value_dict[name]
        self.bindings = name_value_dict 
        for key in self.bindings:
            # If the binding is a function, find its parent. Also, assign all frames that use this code to have self as a parent.
            if callable(self.bindings[key]) and id(self.bindings[key]) not in codestrID_parent_dict:
                code_ID = id(self.bindings[key].__code__)
                codestrID_parent_dict[code_ID] = "Global" if self.index == "Global" else "f" + str(self.index)
                if code_ID in codestrID_frame_dict:
                    for frame in codestrID_frame_dict[code_ID]:
                        frame.set_parent(self)
                        self.add_child(frame)
                    
    
    def set_name(self, name):
        self.__name__ = name

    def set_parent(self, parent):
        self.parent = parent
        self.json_name = self.__name__ + "#" + parent.__name__ if self.__name__ != "Global" else self.__name__
    
    def add_child(self, child):
        self.children.add(child)
    
    def __str__(self, level=0):
        ret = "\t"*level+repr(self.__name__)+"\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret
    
    def freeze(self):
        return FrozenFrame(bindings = frozenset(item for item in self.bindings.items()), children = frozenset(child.freeze() for child in self.children))

    def __repr__(self):
        return '<frame node representation>'

class FrozenFrame(Frame):

    def __init__(self, bindings=None, children=None):
        self.bindings = bindings
        self.children = children

    def __hash__(self) -> int:
        print("bindings hash:", hash(self.bindings))
        print("children hash:", hash(self.children))
        return hash(self.bindings) + hash(self.children)
    
    def __eq__(self, other): 
        if not isinstance(other, Frame):
            # don't attempt to compare against unrelated types
            return False

        return self.__hash__() == other.__hash__()