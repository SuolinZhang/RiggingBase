"""
Author: Caleb
Date:04/10/2023

Rigging library Setup File
Reading the location of our rigging module scripts.
"""

import sys

TOOLS_PATH = "C:/Coding/rigging_tools/"

sys.path.append(TOOLS_PATH)

sys.dont_write_bytecode = True

import maya.cmds as cmds

if not cmds.commandPort(":4434", query=True):
    cmds.commandPort(name=":4434")
