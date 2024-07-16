"""
mod_wsgi-express start-server wsgi.py --modules-directory /lib64/apache2 --port 3000 --log-to-terminal
"""

import sys
#sys.stdout = sys.stderr
sys.path.insert(0,"/home/cicuser/Projects/eht_website")
#sys.path.insert(0, '/home/ethbot/eht_website')
from app import app
application = app
