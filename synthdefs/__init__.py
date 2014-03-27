import os
import re
import sys

_SYNTHDEF_RE = re.compile("^.+\.scsyndef$")

_SYNTHDEF_DIR = os.path.dirname(os.path.abspath(__file__))

for file_name in os.listdir(_SYNTHDEF_DIR):
    if _SYNTHDEF_RE.match(file_name):
        with open(os.path.join(_SYNTHDEF_DIR, file_name), 'rb') as f:
            synth_name = file_name.split('.')[0]
            setattr(sys.modules[__name__], synth_name, f.read())

del f
del file_name
del os
del re
del synth_name
del sys
