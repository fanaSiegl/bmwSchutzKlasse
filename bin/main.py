# PYTHON script
# -*- coding: utf-8 -*-

'''
bmwSchutzKlasse
===============

Creates sets from given *.xlsx configuration file and after adding entities to these sets, they can be exported into an include file.

Location
--------

BMW>schutzKlasse

Usage
-----

* select configuration *.xlsx file
* create sets
* assign entities to sets
* export include

Requirements
------------

.. warning::
    
    Given configuration file must be in the standard format.
    
* designed for ANSA V.19.1.1

'''

#=========================== to be modified ===================================

BUTTON_NAME = 'BMW'
BUTTON_GROUP_NAME = 'schutzKlasse'
DOCUMENTATON_GROUP = 'ANSA tools'
DOCUMENTATON_DESCRIPTION = 'ANSA button for Schutz Klasse sets/include definition.'

#==============================================================================

DEBUG = 0

#==============================================================================

import os
import sys
from traceback import format_exc
import tempfile

import ansa
from ansa import base, guitk, constants, utils

PATH_SELF = os.path.dirname(os.path.realpath(__file__))

ansa.ImportCode(os.path.join(PATH_SELF, 'domain', 'util.py'))

#==============================================================================

class SetDefinition(object):
		
	ID_OFFSET = 100
	
	def __init__(self, parentApplication, attributes):
		
		self.parentApplication = parentApplication
		self._attributes = attributes
		self.id = self._attributes['id']
		self.setEntity = None
		self.content = list()
		
		self.tableColumnLabels = parentApplication.tableColumnLabels
	
	#--------------------------------------------------------------------------
	
	def getName(self, includeId=True):
		
		nameParts = []
		for attrName in self.tableColumnLabels[1:]:
			attrValue = self._attributes[attrName]
			if attrValue is None or len(attrValue) == 0:
				continue
			
			nameParts.append(str(attrValue))
		
		if includeId:
			return '%i;' % self.id + '_'.join(nameParts)
		else:
			return '_'.join(nameParts)
			
	#--------------------------------------------------------------------------
	
	def getSurfaceDefinition(self):
		
		''' *SURFACE, NAME=G"+set+", TYPE=ELEMENT'''
		
		return '*SURFACE, NAME=G%s, TYPE=ELEMENT\nS%s,\n' % (self.getName(), self.getName())
	
	#--------------------------------------------------------------------------
	
	def getSetDefinition(self):
						
		return '*ELSET, ELSET=S%s\n' % self.getName() + ''.join(self.content)
		
	#--------------------------------------------------------------------------
	
	def getOutputForceDefinition(self):
		
		return '*CONTACT OUTPUT, SURFACE=G%s\nCFORCE,\n' % self.getName()
	
	#--------------------------------------------------------------------------
	
	def getOutputEnergyDefinition(self):
		
		return '''*CONTACT OUTPUT, SURFACE=G%s
CFN
CFNM,
*ENERGY OUTPUT, ELSET=S%s
"ALLIE,
''' % (self.getName(), self.getName())
	
	#--------------------------------------------------------------------------
	
	def createEntity(self):
		
		fields = {
			'Name' : self.getName(False),
			'Output as:' : 'Set',
			'OUTPUT TYPE' : 'ELSET'
			}
		self.setEntity = base.CreateEntity(constants.ABAQUS, 'SET', fields, include=self.parentApplication.include)
		
		if self.setEntity is not None:
			base.SetEntityId(self.setEntity, self.id)
	
	#--------------------------------------------------------------------------
	
	def identifyEntity(self):
		
		self.setEntity = base.GetEntity(constants.ABAQUS, 'SET', self.id)
		
	#--------------------------------------------------------------------------
	
	def addContentLine(self, line):
		
		self.content.append(line)
		

#==============================================================================

class SchutzKlasseSetsCreator(object):
	
	DEFINITION_FILE_NAME = 'E_E_Komponenten_G60PHEV_AWD_VL-VKBG.xlsx'
	LABELS_ROW_NO = 0
	
	def __init__(self):
		
		self.setItems = list()
		self.inputConfigFile = None
		
	#--------------------------------------------------------------------------
	
	def setConfigFilePath(self, inputConfigFile):
		
		self.inputConfigFile = inputConfigFile
			
	#--------------------------------------------------------------------------
				
	def createSets(self):
		
		self.createInclude()
		self.readDefinition()
		
		info = list()
		for setItem in self.setItems:
			 setItem.createEntity()
			 info.append(setItem.getName(False))
		
		showInfoMessage('Sets created:\n'+'\n'.join(info))
	
	#--------------------------------------------------------------------------
	
	def identifySets(self):
		
		# identify entities
		setEntities = list()
		setDefinitions = dict()
		for setItem in self.setItems:
			 setItem.identifyEntity()
			 
			 if setItem.setEntity is not None:
				 setEntities.append(setItem.setEntity)
				 setDefinitions['*ELSET, ELSET=%s' % setItem.getName(False).strip()] = setItem
			 
		# identify include
		self.createInclude()
		
		base.AddToInclude(self.include, setEntities)
		
		tempName = tempfile.NamedTemporaryFile(suffix='.inc').name
		
		# output include
		ret = base.OutputAbaqus(
			filename=tempName,
			write_comments='none',
			include=self.include)
		
		if ret:
			fi = open(tempName, 'rt')
			lines = fi.readlines()
			
			currentSetItem = None
			for line in lines:
				if line.startswith('*'):
					if line.strip() in setDefinitions.keys():
						currentSetItem = setDefinitions[line.strip()]
						continue
					else:
						currentSetItem = None
					
				if currentSetItem is not None:
					currentSetItem.addContentLine(line)
				
			fi.close()
		else:
			showCriticalMessage('Something went wrong with the include output.\nPlease output include with sets manually.')
		
		if os.path.exists(tempName):
			os.remove(tempName)
			
	#--------------------------------------------------------------------------
	
	def createInclude(self):

		fields = {'Name' : 'sets_for_schutzklasse'}
		self.include = base.CreateEntity(constants.ABAQUS, 'INCLUDE', fields)
		
	#--------------------------------------------------------------------------

	def readDefinition(self):
		
#		if DEBUG:
#			self.inputConfigFile = os.path.join(util.PATH_RES, self.DEFINITION_FILE_NAME)
			
		xl_element = utils.XlsxOpen(self.inputConfigFile)
		sheetName = utils.XlsxGetSheetName(xl_element, 0)
		
		rowCount, colCount = utils.XlsxMaxSheetCell(xl_element, sheetName)
		
		self.definition = dict()
		self.tableColumnLabels = list()
		for rowNo in range(rowCount):
			descriptionNo = utils.XlsxGetCellValue(xl_element, sheetName, rowNo , 0)
			
			# skip empty rows
			if descriptionNo is None or len(descriptionNo) == 0:
				continue
			
			# identify table labels
			if rowNo == self.LABELS_ROW_NO:
				for cNo in range(colCount):
					cellValue = utils.XlsxGetCellValue(xl_element, sheetName, rowNo , cNo)
					if cellValue is None or len(cellValue) == 0:
						break
					self.tableColumnLabels.append(cellValue)
				continue
			
			self.definition[descriptionNo] = dict()
			for columnNo, label in enumerate(self.tableColumnLabels):
				
				cellValue = utils.XlsxGetCellValue(xl_element, sheetName, rowNo , columnNo)			
				
				# set id
				if columnNo == 0:
					self.definition[descriptionNo]['id'] = int(cellValue) + SetDefinition.ID_OFFSET
				
				# rename Schutzklasse
				if label.strip().lower() == 'schutzklasse':
					temp = int(''.join(filter(str.isdigit, cellValue)))
					cellValue = cellValue + "_<schutzPostfix"+str(temp)+">"
				
				self.definition[descriptionNo][label] = cellValue.strip().replace(' ', '_')
				
			setItem = SetDefinition(self, self.definition[descriptionNo])
			self.setItems.append(setItem)
		
		utils.XlsxClose(xl_element)
		
	#--------------------------------------------------------------------------

	def writeInclude(self, fileName):
		
		self.readDefinition()
		self.identifySets()
					
#		fileName = os.path.join(util.PATH_RES, 'schutz.inc')
		f = open(fileName,"w+")
		
		f.write(util.DEFINITION_STRING_PARAMETERS)
		f.write(util.DEFINITION_STRING_SURFACE)
		
		for setItem in self.setItems:
			 f.write(setItem.getSurfaceDefinition())
			 		
		f.write(util.DEFINITION_STRING_SET)
		
		for setItem in self.setItems:
			 f.write(setItem.getSetDefinition())
				
		f.write(util.DEFINITION_STRING_STEP)
		f.write(util.DEFINITION_STRING_STEP_TYPE)
		f.write(util.DEFINITION_STRING_STEP_OUTPUT_FILED)
				
		for setItem in self.setItems:
			 f.write(setItem.getOutputForceDefinition())
		
		f.write(util.DEFINITION_STRING_STEP_OUTPUT_HISTORY)
		
		for setItem in self.setItems:
			 f.write(setItem.getOutputEnergyDefinition())
		
		f.write("*END STEP")
		f.close()  

# ==============================================================================

class SchutzKlasseDialog(object):
	
	TITLE = 'Schutz Klasse'
	WIDTH = 600
	HEIGTH = 150
	
	def __init__(self):
		
		revision, modifiedBy, lastModified = util.getVersionInfo()
		
		self.dialog = guitk.BCWindowCreate("%s (%s)" % (self.TITLE, revision), guitk.constants.BCOnExitDestroy)
		
		self.creator = SchutzKlasseSetsCreator()
		
		guitk.BCWindowSetInitSize(self.dialog, self.WIDTH, self.HEIGTH)
		guitk.BCWindowSetSaveSettings(self.dialog, False)
		
		self.mainLayout = guitk.BCBoxLayoutCreate(self.dialog, guitk.constants.BCVertical)
		
		# input path
		configFileLayout = guitk.BCBoxLayoutCreate(self.dialog, guitk.constants.BCHorizontal)
		guitk.BCLabelCreate(configFileLayout, 'Input configuration file')
		
		self.inputConfigFileLineEdit = guitk.BCLineEditPathCreate(configFileLayout, guitk.constants.BCHistoryFiles,
			os.path.dirname(base.DataBaseName()), guitk.constants.BCHistorySelect, 'schutzKlasseInputConfigFile')
		guitk.BCLineEditPathSetFilter(self.inputConfigFileLineEdit, 'MS Excel files (*.xlsx)')
		
#		# output path
#		configFileLayout = guitk.BCBoxLayoutCreate(self.dialog, guitk.constants.BCHorizontal)
#		guitk.BCLabelCreate(configFileLayout, 'Output include file')
#		self.outputIncludeFileLineEdit = guitk.BCLineEditPathCreate(configFileLayout, guitk.constants.BCHistoryFiles,
#			os.path.dirname(base.DataBaseName()), guitk.constants.BCHistorySaveAs, 'schutzKlasseOutInclude')
#		guitk.BCLineEditPathSetFilter(self.outputIncludeFileLineEdit, 'ABAQUS (*.inc)')
		
		dbb = guitk.BCDialogButtonBoxCreate(self.dialog)
		acceptButton = guitk.BCDialogButtonBoxGetAcceptButton(dbb)
		guitk.BCButtonSetText(acceptButton, 'Create sets')
		b = guitk.BCPushButtonCreate(dbb, 'Export include', self.exportInclude, None)
		guitk.BCDialogButtonBoxAddButton(dbb, b)
		
		guitk.BCWindowSetAcceptFunction(self.dialog, self.createSets, None)
		
		guitk.BCShow(self.dialog)
	
	#--------------------------------------------------------------------------

	def exportInclude(self, b, data=None):
		
		path = guitk.BCLineEditPathLineEditText(self.inputConfigFileLineEdit)
		if len(path) == 0 or not os.path.exists(path):
			
			showCriticalMessage('Given configuration file does not exist!')
			return
		else:
			self.creator.setConfigFilePath(path)
		
		path = utils.SelectSaveFileIn(os.path.dirname(base.DataBaseName()), 'ABAQUS (*.inc)')
		if len(path) == 0:
			return
			
		self.creator.writeInclude(path[0])
		
		showInfoMessage('Saved to: "%s"' % path[0])
		
		guitk.BCDestroyLater(self.dialog)
	
	#--------------------------------------------------------------------------

	def createSets(self, w, data=None):
		
		path = guitk.BCLineEditPathLineEditText(self.inputConfigFileLineEdit)
		if len(path) == 0 or not os.path.exists(path):
			
			showCriticalMessage('Given configuration file does not exist!')
			return 0
		
		self.creator.setConfigFilePath(path)
		self.creator.createSets()
		
		return 1
		

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
		project = SchutzKlasseDialog()
	except Exception as e:
		print(format_exc())
		showCriticalMessage(str(e))

#==============================================================================

if __name__ == '__main__' and DEBUG:
	main()
