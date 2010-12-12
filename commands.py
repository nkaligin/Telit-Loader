import sys,os
import optparse
import setPort
import time

global fileInput
global fileLength
global fileName
fileName=None
fileLength=None
fileInput=None
#Gets file name from options##############################################
def getFile():
	global fileInput
	global fileLength
	global fileName
	parser = optparse.OptionParser()		#create and init optionParser
	parser.add_option("-f", "--file",\
		action = "store", type = "string",\
		dest = "FILE", help="py file name")
	(options, args) = parser.parse_args()		#parse options
	#errorcheck options
	if options.FILE is None:
		print "You must specify a file EG. make upload FILE=myFile.py"
		sys.exit(1) #bad for UNIX
	else:
		fileName = options.FILE			#the name of the file
		print "Opening:"+ fileName		
		file = open(fileName,'r')
		fileInput = file.readlines()
		fileLength = os.path.getsize(fileName)
		######***TO COMPENSATE FOR FILE SIZE BUG***########
		fileLength += 20
##########################################################################

#Sends File###############################################################
def writeFile():
	global fileInput
	global fileLength
	global fileName
	
	print "writing file:"
	print fileName
	print fileLength
		
	writeCommand= "AT#WSCRIPT=%s,%i\r\n" % (fileName,fileLength)
	print "Sending:" + writeCommand
	setPort.serialOpenCheck()			#open serial connection send AT to check
	setPort.telitPort.flushInput()			#get rid of junk
	setPort.telitPort.write(writeCommand)
	input = setPort.getReply()			#from setPort
	if ">>>" not in input:
		print "didn't get >>>??"
		print input		
		sys.exit(1)
	print"START FILE#########"
	lineMarker=0
	for line in fileInput:
		try:	#two from back is /n/l
			if(line[-1:] == "\r\n"):
				writeLine=line
			#it is somthing else append \r\n
			else:
				writeLine=line[:-1] + "\r\n"
			#write out to port
			setPort.telitPort.write(writeLine)
			#print what we wrote
			print "%i: %s" % (lineMarker,writeLine)
			lineMarker+=1
			time.sleep(.1) #sleep a bit to see the line
		except setPort.serial.serialutil.SerialTimeoutException:
			print "serial timed out on line " + lineMarker	
			setPort.serialClose()
			sys.exit(1)
	input = setPort.getReply()
	for line in input:
		if "OK\r\n" in line:
			print "loaded OK"
			break
	else:
		print input
	setPort.telitPort.flush()
	print"END FILE###########"
########################################################################


#DELETE FILES############################################################
def deleteFile():
	global fileLength
	global fileName
	
	setPort.serialOpenCheck()				#open serial connection send AT to check
	deleteCommand= "AT#DSCRIPT=%s\r\n" % (fileName)
	if ".py" in fileName:
		print "\nDELETING .py file:"
		#delete both files .py and .pyo
		print "Sending: " + deleteCommand
		setPort.telitPort.flush()
		setPort.telitPort.write(deleteCommand)
		input = setPort.getReply()
		for lines in input:
			if "OK" in lines:
				print "FOUND AND DELETED:" +fileName
				break	
			elif "ERROR" in lines:
				print "didn't find .py file: " +fileName
				print lines
				break
		#delete .pyo
		print "\nDELETING .pyo file:"
		deleteCommand= "AT#DSCRIPT=%so\r\n" % (fileName) #add 'o' for pyo
		print "Sending: " + deleteCommand
		setPort.telitPort.flushInput()
		setPort.telitPort.write(deleteCommand)
		input = setPort.getReply()
		for lines in input:
			if "OK" in lines:
				print "FOUND AND DELETED:" +fileName
				break
			elif "ERROR" in lines:
				print "didn't find .pyo file: " +fileName
				print lines
				break
	setPort.serialClose()
########################################################################################


#list Files##############################################################################
def listFiles():
	global fileLength
	global fileName
	
	if fileName is None:				#set impossible
		fileName="spoogert"
		fileLength=1000000000
	setPort.serialOpenCheck()			#open serial connection send AT to check
	listCommand= "AT#LSCRIPT\r\n" 
	print "Listing current files:"
	print "Sending: " + listCommand
	setPort.telitPort.flush()
	setPort.telitPort.write(listCommand)
	input = setPort.getReply()
	foundFile="false"
	for line in input:
		print line
		if "#LSCRIPT: \"%s\",%i" % (fileName,fileLength) in line:
			print "*******************************FOUND FILE->" +fileName
			foundFile="true"	
	if foundFile == "true":
		print "#########################################"
		print "FILE: " +fileName + " is stored on Telit.."
		print "#########################################"
	
	setPort.serialClose()
##########################################################################################

#READ FILE###############################################################################
def readFile():
	global fileName
	setPort.serialOpenCheck()			#open serial connection send AT to check
	readCommand = "AT#RSCRIPT=\"%s\"\r\n" % (fileName)
	print "Reading file: " + fileName
	print "Sending: " + readCommand
	setPort.telitPort.flush()
	setPort.telitPort.write(readCommand)
	input = setPort.getReply()
	lineMarker=0
	for line in input:
		time.sleep(.1)
		print "%i: %s"%(lineMarker,line)
		lineMarker+=1
	
###########################################################################################




#test			
getFile()
#readFile()
#listFiles()
#deleteFile()
writeFile()
#print fileLength
#print fileInput





