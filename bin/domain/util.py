# PYTHON script
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys
import configparser
import numpy as np
import subprocess

#==============================================================================

PATH_BIN = os.path.normpath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)),'..'))
PATH_INI = os.path.normpath(os.path.join(PATH_BIN,'..', 'ini'))
PATH_DOC = os.path.normpath(os.path.join(PATH_BIN,'..', 'doc'))
PATH_RES = os.path.normpath(os.path.join(PATH_BIN,'..', 'res'))
PATH_ICONS = os.path.join(PATH_RES, 'icons')

VERSION_FILE = 'version.ini'

#==============================================================================

def getVersionInfo():

    SECTION_VERSION = 'VERSION'
     
    config = configparser.ConfigParser()
     
    cfgFileName = os.path.join(PATH_INI, VERSION_FILE)
    config.read(cfgFileName)
         
    revision = config.get(SECTION_VERSION, 'REVISION')
    modifiedBy = config.get(SECTION_VERSION, 'AUTHOR')
    lastModified = config.get(SECTION_VERSION, 'MODIFIED')
 
    return revision, modifiedBy, lastModified

#==============================================================================

def runSubprocess(command, cwd=None):
    
    process = subprocess.Popen(
        command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        cwd=cwd)
       
    if stdout is not None:
        stdout = stdout.decode("ascii",errors="ignore")
    if stderr is not None:
        stderr = stderr.decode("ascii",errors="ignore")
    
    return stdout, stderr

#==============================================================================

DEFINITION_STRING_SURFACE = '''**
** SURFACE DEFINITIONS 
**
'''
DEFINITION_STRING_SET = '''** 
** SETS
**
'''
DEFINITION_STRING_STEP = '''**
** Step
**
'''
DEFINITION_STRING_STEP_TYPE = '''*STEP, NAME = Step_Schutzklassensets
*DYNAMIC, EXPLICIT, ELEMENT BY ELEMENT
,             0.15
'''
DEFINITION_STRING_STEP_OUTPUT_FILED = '*OUTPUT, FIELD, TIME INTERVAL=0.004\n'
DEFINITION_STRING_STEP_OUTPUT_HISTORY = '*OUTPUT, HISTORY, TIME INTERVAL=0.0001, FILTER=ANTIALIASING\n'
DEFINITION_STRING_PARAMETERS = '''*PARAMETER
QI_INCLPRE = 0
QI_SQMS = 1.02
QI_NK = 1548406903
schutzklasse1 = 0
schutzklasse2 = 5
schutzklasse3 = 20
schutzklasse4 = 25
schutzklasse5 = -1000
schutzklasse6 = 1000
**
** Lastfallabhaengiger Zuendzeitpunkt
**
** Pfahl Front
**zzpSchutzklasse = 34
** USNCAP
**zzpSchutzklasse = 10
** FMVSS301
zzpSchutzklasse = 25
** SOL
**zzpSchutzklasse = 25
** FOO
**zzpSchutzklasse = 15
**
** Set Postfix
**
schutzPostfix1 = schutzklasse1 + zzpSchutzklasse
schutzPostfix2 = schutzklasse2 + zzpSchutzklasse
schutzPostfix3 = schutzklasse3 + zzpSchutzklasse
schutzPostfix4 = schutzklasse4 + zzpSchutzklasse
schutzPostfix5 = schutzklasse5 + zzpSchutzklasse
schutzPostfix6 = schutzklasse6 + zzpSchutzklasse
'''