# atod
Atod (standing for Alexa to Dictionary) is a python script which analizes the Alexa top 1 million and creates a dictionary and a stats file. The idea is using the Dictionary as input during the Information Gathering phase and the stats file for analysis purposes.

The script is cross platform Windows/Linux (should be Mac as well but I didn't tested it) since it has been developed in Python. The only thing you need from this rep is the .py file even though I have uploaded here the dictionary and stat file as a result of the script execution (Date 17/09/2016).

# Why atod?
I developed this first version keeping in mind the idea of using the resultant dictionary for brute forcing during my pentests. Hope it will be useful as well for you as a complement of the ones available with other tools as Skipfish, Dirbuster, ZAP or Burp.  But the results of this scripts can be brough much further... I hope to have time for a version 2 including more features... :)

# What atod exactly does?
The functionality embedded in atod enables the automation of the next process:
1.- Download the Alexa top 1M file
2.- Decompress the file in the current directory
3.- Create a queue to look using both schemes (http and https) for the robots.txt file. It will take into account the "LIMIT" constant to analyse only the number of URLs indicated in it
4.- Run NPROCES processes, being NPROCESS another constant you can edit at your convenience
5.- Analyse each robots.txt file for the Disallowed folders
6.- Build two different files, one to use as a dictionary and the other one for analytics purposes including the number of times each folder have been found as disallowed
7.- Before writing all the folders down to file a cleaning post-processing is performed, to avoid wild cards and malformed entries in the robots.txt causing pointless information in the files.
8.- The script wait all processes to finish and ends.

# How to run
Atod is not parametrized, I did it as an exercise of learning python so once you download it just grant running permission and execute:

]$ ./atod

Atod is initaly configured to analyse the Alexa top 1000 and running 10 paralel processes so you have a good base in a matter of minutes. If you want to go further just access the script using your favourite editor and modify the next parameters:

LIMIT = X //X being the number of URLs you want to analyze once the alexa file is downloaded
NPROCESS = Y //Y being the number of parallel processes you want to run

# How it performed for me
Taking into account that my laptop is quite latest (16Gb RAM, SSD and core i7) and my internet connection is not bad (20Mbps), it tooks ~6 hours to pull all the information from the alexa top 1 million using 150 paralel processes.

You can have a consistent analysis using much more less than that. I tried with all the file to push the script to the limits but a configuration with 50 parallel processes and a limit of 100K URLs will give you a great dictionary and results for analysis in ~1 hour

# To take into account

- Be aware that increasing the number of processes will cause as well an increase in the time the script takes waiting for them to stop.
- Mind as well that the script have been developed with resilience in mind. That means some errors are already treated in the script and you will have meaninfull results even if some IOErrors are received by the script. It will finish and gives you its best

