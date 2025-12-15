import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "packages")

if os.path.isdir(PKG) and PKG not in sys.path:
    sys.path.insert(0, PKG)
