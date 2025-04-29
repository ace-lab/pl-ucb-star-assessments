import Qgen_customization
import os
import contextlib
def generate(data):
    with open(os.devnull, 'w') as devnull:
        with contextlib.redirect_stdout(devnull):
            try: 
                # These two 'with' statements silence the execution so no print statements are printed, which can bug out prarielearn. 
                with open(os.devnull, 'w') as devnull:
                    with contextlib.redirect_stdout(devnull):
                        data["params"]["codestring"] = Qgen_customization.generateQ(data['variant_seed'])
            except:
                data["params"]["codestring"] = "Question generation failed. Question file may be malformed."
    return data
