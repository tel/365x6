import sys, os
INTERP = './env/bin/python'
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd)

from app365.app import app as application
