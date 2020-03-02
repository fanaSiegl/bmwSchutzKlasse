# PYTHON script
# -*- coding: utf-8 -*-

'''
Project name
============

Project function description.

* does requires something
* does something
* creates something as an output

Location
--------

buttonGroupName>buttonName

Usage
-----

* click here
* click there
* click there

Requirements
------------

.. warning::
    
    Requires something
    
* designed for ANSA V.19.1.1

'''

#=========================== to be modified ===================================

BUTTON_NAME = 'buttonName'
BUTTON_GROUP_NAME = 'buttonGroupName'
DOCUMENTATON_GROUP = 'ANSA tools'
DOCUMENTATON_DESCRIPTION = 'Python application one line description.'

#==============================================================================

DEBUG = 1

#==============================================================================

import os
import sys
from traceback import format_exc

import ansa
from ansa import base, guitk, constants

PATH_SELF = os.path.dirname(os.path.realpath(__file__))

ansa.ImportCode(os.path.join(PATH_SELF, 'domain', 'util.py'))

#==============================================================================

class Project(object):

	APPLICATION_NAME = 'New project name'

	def __init__(self):

		self.method1()

	#--------------------------------------------------------------------------

	def method1(self):
		
		showInfoMessage('%s\n%s' % (self.APPLICATION_NAME, util.getVersionInfo()))


# ==============================================================================

def showCriticalMessage(message):

	messageWindow = guitk.BCMessageWindowCreate(guitk.constants.BCMessageBoxCritical, message, True)
	guitk.BCMessageWindowSetRejectButtonVisible(messageWindow, False)
	guitk.BCMessageWindowExecute(messageWindow)

# ==============================================================================

def showInfoMessage(message):

	messageWindow = guitk.BCMessageWindowCreate(guitk.constants.BCMessageBoxInformation, message, True)
	guitk.BCMessageWindowSetRejectButtonVisible(messageWindow, False)
	guitk.BCMessageWindowExecute(messageWindow)
	
#==============================================================================
@ansa.session.defbutton(BUTTON_GROUP_NAME, BUTTON_NAME, __doc__)
def main():

	main.__doc__ = __doc__

	try:
		project = Project()
	except Exception as e:
		print(format_exc())
		showCriticalMessage(str(e))

#==============================================================================

if __name__ == '__main__' and DEBUG:
	main()
