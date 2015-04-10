#!/usr/bin/python

# Created on: 2015.04.09 
# Author: Carlo Artieri

##############################
# HISTORY AND THINGS TO FIX  #
##############################
#2015.04.09 - Initial script
#
#2015.04.10	- Functional, nohups curl shell scripts and resumes upon restart.
#			- FIX:	Don't print nonsense defaults
#			- ADD: --clean option to remove intermediate files?
#			  

###########
# MODULES #
###########
import sys			#Access to simple command-line arguments
sys.path.append('/Users/carloartieri/bin/python') #Set python path for common functions
import argparse		#Access to long command-line parsing	
import datetime		#Access to calendar/clock functions
import re			#Access to REGEX splitting
import math			#Access to math functions
import random		#Access to random number generator
import subprocess
#import common		#My custom common python scripts

##########################
# COMMAND-LINE ARGUMENTS #
##########################

epilog = """\
This script splits a list of file locations (on remote servers) into a specified number of curl
download shell scripts, which are simultaneously run in 'nohup' mode. Each shell script will 
have the name:

	[DESTINATION FOLDER_]curl_list_[#].sh

Each will create an empty file of format [DESTINATION FOLDER_]curl_list_[#].sh_done when all 
files have been successfully downloaded. Note that if the same command is rerun before the 
have completed downloading, they will resume from their current position (curl option '-C -').

More detailed description of options follows:
-c/--concurrent 
	The number of concurrent shell scripts to execute.
-d/--dest
	The shell scripts will tell curl to download to the specified location. If this option is
	unspecified, files download to the current directory.
	
"""
class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(description='Create shell scripts to multiplex curl downloading.', add_help=False, epilog=epilog, formatter_class=CustomFormatter)
req = parser.add_argument_group('Required arguments:')
req.add_argument('-i','--inlist', action="store", dest="list", help='List of file addresses from which to curl', required=True, metavar='')
opt = parser.add_argument_group('Optional arguments:')
opt.add_argument('-c','--concurrent', action="store", dest="con", type=int, help='Number of concurrent downloads [default: 5]', default=5, metavar='')
opt.add_argument('-d','--dest', action="store", dest="dest", help='Specify destination folder [instead of current]', metavar='')
#opt.add_argument('-x','--clean', action="store_true", dest="clean", help='After run completes, run -x/--clean to remove intermed files')
opt.add_argument("-h", "--help", action="help", help="show this help message and exit")
args = parser.parse_args()

#############
# FUNCTIONS #
#############

##########
# SCRIPT #
##########

#If the destination folder has a trailing slash, axe it.
print args.dest + ' ',
if args.dest[-1] == '/':
	args.dest = args.dest[:-1]

#Check if args.dest has a trailing slash and if so remove

#Open the list of web addresses to curl from and store them in a list
file_list = []
infile = open(args.list, 'r')
for line in infile:
	if re.match('^#', line):	#Going to skip commented lines
		continue
	line = line.rstrip('\n')
	file_list.append(line)
infile.close()

#Split the list into args.con sublists and run them independently
files_per_con = int(len(file_list)/float(args.con)+1)	#Always round up against stragglers

count = 0
list_count = 0
if args.dest is not None:
	file_out = args.dest + '_curl_list_' + str(list_count) + '.sh'
else:
	file_out = 'curl_list_' + str(list_count) + '.sh'
shell_script = open(file_out, 'w')
launched = 0
for i in file_list:
	if count == files_per_con - 1:
		if args.dest is not None:
			#Need to split by slash and get the file name.
			path_split = i.split('/')
			shell_script.write('curl -o ' + args.dest + '/' + str(path_split[-1]) + ' -C - ' + str(i) + '\n')
			shell_script.write('touch ' + file_out + '_done\n') #The list will tell us when done
			shell_script.close()
		else:
			shell_script.write('curl -C - -O' + str(i) + '\n')
			shell_script.write('touch ' + file_out + '_done\n') #The list will tell us when done
			shell_script.close()
		#Launch the shell script
		subprocess.call(['chmod', '777', file_out])	#chmod the shell script
		subprocess.Popen(['nohup', './' + file_out, '&'])	#Nohup the shell script
		count = 0
		list_count += 1
		launched = 1
		if file_list.index(i) != len(file_list) - 1:
			if args.dest is not None:
				file_out = args.dest + '_curl_list_' + str(list_count) + '.sh'
			else:
				file_out = 'curl_list_' + str(list_count) + '.sh'
			shell_script = open(file_out, 'w')
	else:
		if args.dest is not None:
			#Need to split by slash and get the file name.
			path_split = i.split('/')
			shell_script.write('curl -o ' + args.dest + '/' + str(path_split[-1]) + ' -C - ' + str(i) + '\n')
		else:
			shell_script.write('curl -C - -O' + str(i) + '\n')
		count += 1
		launched = 0

if launched == 0:
	shell_script.write('touch ' + file_out + '_done\n') #The list will tell us when done
	shell_script.close()
	subprocess.call(['chmod', '777', file_out])	#chmod the shell script
	subprocess.Popen(['nohup', './' + file_out, '&'])	#Nohup the shell script



















