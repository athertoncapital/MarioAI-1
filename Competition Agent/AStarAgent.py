import sys
import os

import ctypes
from ctypes import *
from ctypes import POINTER
from ctypes import c_int
from ctypes import py_object

from ctypes.util import find_library
from astar import AStar
import numpy

from evaluationinfo import EvaluationInfo

class ListPOINTER(object):
	'''Just like a POINTER but accept a list of ctype as an argument'''
	def __init__(self, etype):
		self.etype = etype

	def from_param(self, param):
		if isinstance(param, (list, tuple)):
#			print "Py: IS INSTANCE"
			return (self.etype * len(param))(*param)
		else:
#			print "Py: NOT INSTANCE"
			return param

class ListByRef(object):
	'''An argument that converts a list/tuple of ctype elements into a pointer to an array of pointers to the elements'''
	def __init__(self, etype):
		self.etype = etype
		self.etype_p = POINTER(etype)

	def from_param(self, param):
		if isinstance(param, (list, tuple)):
			val = (self.etype_p * len(param))()
			for i, v in enumerate(param):
				if isinstance(v, self.etype):
					val[i] = self.etype_p(v)
				else:
					val[i] = v
			return val
		else:
			return param

def from_param(self, param):
	if isinstance(param, (list, tuple)):
		return (self.etype * len(param))(*param)
	else:
		return param


def cfunc(name, dll, result, * args):
	'''build and apply a ctypes prototype complete with parameter flags'''
	atypes = []
	aflags = []
	for arg in args:
		atypes.append(arg[1])
		aflags.append((arg[2], arg[0]) + arg[3:])
	return CFUNCTYPE(result, * atypes)((name, dll), tuple(aflags))

def amiCoSimulator():
	"""simple AmiCo env interaction"""
	print "Py: AmiCo Simulation Started:"
	print "library found: "
	#add syspath
	new_path = os.path.abspath("./").lower()
	java_path = os.path.abspath("C:\\Program Files (x86)\\Java\\jre6\\bin").lower()
	java_path2 = os.path.abspath("C:\\Program Files (x86)\\Java\\jre6\\bin\\client").lower()
	sys.path.append(new_path)
	sys.path.append(java_path)
	sys.path.append(java_path2)
	
	if (sys.platform == 'linux2'):
	##########################################
	# find_library on Linux could only be used if your libAmiCoPyJava.so is
	# on system search path or path to the library is added in to LD_LIBRARY_PATH
	#
	# name =  'AmiCoPyJava'
		# loadName = find_library(name)
		##########################################
		loadName = './libAmiCoPyJava.so'
		libamico = ctypes.CDLL(loadName)
		print libamico
	else: #else if OS is a Mac OS X (libAmiCo.dylib is searched for) or Windows (AmiCo.dll)
		name =  'AmiCoPyJava.DLL'
		loadName = find_library(name)
		print loadName
		libamico = ctypes.CDLL(name)
		print libamico
	
	javaClass = "ch/idsia/benchmark/mario/environments/MarioEnvironment"
	libamico.amicoInitialize(1, "-Djava.class.path=." + os.pathsep +":../lib/jdom.jar")
	libamico.createMarioEnvironment(javaClass)
	
	reset = cfunc('reset', libamico, None, ('list', ListPOINTER(c_int), 1))
	getEntireObservation = cfunc('getEntireObservation', libamico, py_object,
								 ('list', c_int, 1),
								 ('zEnemies', c_int, 1))
	performAction = cfunc('performAction', libamico, None, ('list', ListPOINTER(c_int), 1))
	getEvaluationInfo = cfunc('getEvaluationInfo', libamico, py_object)
	getObservationDetails = cfunc('getObservationDetails', libamico, py_object)
	
	agent =AStar()

	options = ""
	if len(sys.argv) > 1:
		options = sys.argv[1]

	print "options: ", options
	k = 1
	seed =0
	print "Py: ======Evaluation STARTED======"
	totalIterations = 0
	for i in range(k, k+100):
		options1 = options + "-ls " + str(seed)+" -fps 30 -ld 0"
		reset(options1)
		obsDetails = getObservationDetails()
		agent.setObservationDetails(obsDetails[0], obsDetails[1], obsDetails[2], obsDetails[3])
		while (not libamico.isLevelFinished()):
			totalIterations +=1 
			libamico.tick();
			obs = getEntireObservation(1, 0)
			agent.integrateObservation(obs[0], obs[1], obs[2], obs[3], obs[4]);
			action = agent.getAction()
			performAction(action);
		evaluationInfo = getEvaluationInfo()
		print evaluationInfo
		seed += 1
def printenvobv(envlist):
	i=0
	temp = []
	while i<len(envlist):
		temp.append(envlist[i])
		if len(temp) == 19:
			print temp
			temp = []
		i +=1
if __name__ == "__main__":
	amiCoSimulator()


