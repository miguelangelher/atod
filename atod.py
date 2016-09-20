#!/usr/bin/env python

import urllib2
from multiprocessing import Process, Manager, Queue, Lock
import sys
import zipfile
import operator

FOLDER = "/robots.txt"
FILEZIP = "alexa_top_1m.zip"
ALEXAURL = "http://s3.amazonaws.com/alexa-static/top-1m.csv.zip"
EXTRACTDIR = "."
NPROCES = 10 #This parameter is the number of processes you want to run
FILENAME = "top-1m.csv"
LIMIT = 1000	#This parameter is the number of URLs you want to analyze for http and https
OUTFILENAME = "alexa_dict.txt"
STATFILENAME = "alexa_stats.txt"

'''
This method retrieves and decompress the alexa file, as a result a file with name top-1m.csv is downloaded
in the current folder
'''
def downloadAlexaFile(url, zipName):
	try:

		print "[+] Retrieving alexa top 1m file from " + url
		print "[+] Please, wait while download is in process, this should take less than 1 minute...",
		sys.stdout.flush()
		f = urllib2.urlopen(url)
		data = f.read()
		with open(zipName, "wb") as code:
			code.write(data)
		print "[ OK ]"

		print "[+] Unziping the file...",
		with zipfile.ZipFile('alexa_top_1m.zip', "r") as z:
			z.extractall(".")
		print "[ OK ]"

	except:
		print "[-] Error while retrieving and unziping the code...exiting"
		exit(0)

'''
This method will return a queue with all the URLs to be tested for the robots.txt file. It receives as an input the
name of the alexaFile once it has been decompressed.
'''	
def initQueue(alexaFile, limitUrls):
	
	fd = open(alexaFile,"r")
	try:
		urlsQueue = Queue()
		counter = 0
		for line in fd.readlines():
			domain = line.split(',')[1].strip()
			url = "https://www." + domain + FOLDER
			urlsQueue.put(url)
			url = "http://www." + domain + FOLDER #possibly some of them wont be available through https ;)
			urlsQueue.put(url)
			counter = counter + 1
			if counter > limitUrls:
				break

		return urlsQueue
	except:
		print "[-] Error during queue initialization...exiting"
		exit(0)
	finally:
		fd.close()
'''
This method will be executed in pararell for all the Processes. The idea is having only the queue and the dictionary
as shared objects. The access to the queue is performed in mutual exclussion but the dictionary, even when it comes
from a Manager and it is shared memory, should be regulated by a semaphore.
'''
def retrieveDisallowed(queueUrls, dictDisallow, dictionaryLock, screenLock):
	while not queueUrls.empty():		
		try:
			url = queueUrls.get()
			res = urllib2.urlopen(url,timeout=0.5)
			con = res.read().split('\n')
			
			screenLock.acquire()			
			sys.stdout.write("[i] retrieving disallowed folders. Current queue size: %d \r" % (queueUrls.qsize()))
			sys.stdout.flush()
			screenLock.release()
			
			for line in con:	
				if line.find("Disallow") >= 0:
					disfol = line.split(" ")[1].strip()
					dictionaryLock.acquire()
					if disfol != "" and disfol.find("Disallow") < 0: #sometimes the robots txt could give you Disallow as a value, dropping them from the list
						if disfol not in dictDisallow:						
							dictDisallow[disfol] = 1					
						else:						
							dictDisallow[disfol] += 1
			
					dictionaryLock.release()
		except:
			continue

'''
This method will create two files, one for the stats and another one to use with dirbuster, ZAP, dirb, or any other
bruteforce tool. 
'''
def dumpToFile(sortedTupleList,fileName,statFileName):
	fd = open(fileName,"w")
	fs = open(statFileName,"w")
	try:
		addedFolders = []
		for sortedTuple in sortedTupleList:
			disFolder = sortedTuple[0]
			nTimes = sortedTuple[1]
			try:
				fs.write("%s,%d\n" % (disFolder,nTimes))
				#eliminating paths never existing directly through bruteforcing
				cleanFolder = disFolder.replace("/*","").replace("*","") 
				if cleanFolder not in addedFolders:
					fd.write(cleanFolder+"\n")
					addedFolders.append(cleanFolder)
			except:
				print "[+] Problems found trying to write down to file the folder:" + disFolder
				continue

	except:
		print "[-] The script couldn't dump all the results to the files...check for the exiting"

	finally:
		fd.close()
		fs.close()

if __name__ == '__main__':

	print "[+] Initializing variables...",
	mgr = Manager()
	qUrls = Queue()
	dictDis = mgr.dict()
	dictLock = Lock()
	scrLock = Lock()
	processList = []
	print "[ OK ]"

	downloadAlexaFile(ALEXAURL,FILEZIP)

	print "[+] filling in the queue with the URLs...",
	qUrls = initQueue(FILENAME,LIMIT)
	print "[ OK ]"

	scrLock.acquire() #We need the lock since it is possible another process get the output dirty
	print "[+] Starting %d processes..." % (NPROCES),
	for i in range(NPROCES):
		processList.append(Process(target=retrieveDisallowed, args=(qUrls, dictDis, dictLock, scrLock)))
		processList[i].start()
	print "[ OK ]\n"
	scrLock.release()

	for i in range(NPROCES):
		processList[i].join()

	print "[i] %d different disallowed folders have been found ;)" % len(dictDis)

	print "[+] All processes finished, sorting the dictionary, this may take some time...",
	sys.stdout.flush()
	sortedTupleList = sorted(dictDis.items(), key=operator.itemgetter(1), reverse=True)
	print "[ OK ]"

	print "[+] Writting down to file and eliminating duplicates...",
	sys.stdout.flush()
	dumpToFile(sortedTupleList, OUTFILENAME, STATFILENAME)
	print "[ OK ]"

	print "[i] Mind the number of lines in the dictionary won't match the number of folders retrieved because of the cleaining process"

	print "\n Script by:\t Miguel Angel Hernandez Ruiz"
	print "\n     --> Check the file %s for your new dictionary <--" % (OUTFILENAME)
	print "   --> For statistic analysis view the new file %s <--" % (STATFILENAME)
	print "                --> GREAT DAY FOR HACKING! <--"
	print "   --> visit me on http://plusplussecurity.com/ <--\n"
