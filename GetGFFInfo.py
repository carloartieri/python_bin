#!/usr/bin/python

# Created on: 2015.04.03 
# Author: Carlo Artieri

##############################
# HISTORY AND THINGS TO FIX  #
##############################
#2015.04.03 - Initial script
#
#2015.04.14 - Finished script and tested on GFF file, works
#			- Add in a count of exons for each transcript

###########
# MODULES #
###########
import sys			#Access to simple command-line arguments
import argparse		#Access to long command-line parsing	
import datetime		#Access to calendar/clock functions
import re			#Access to REGEX splitting
import math			#Access to math functions
import random		#Access to random number generator
#sys.path.append('/Users/carloartieri/bin/python') #Set python path for common functions
#import common		#My custom common python scripts

##########################
# COMMAND-LINE ARGUMENTS #
##########################

parser = argparse.ArgumentParser(description='Generates an info table about genes/transcripts within a GFF/GTF annotation file.', add_help=False)
req = parser.add_argument_group('Required arguments:')
req.add_argument('-g','--gff', action="store", dest="gff", help='GFF/GTF file', required=True, metavar='')
req.add_argument('-o','--outfile', action="store", dest="outfile", help='Outfile where info will be stored', required=True, metavar='')
opt = parser.add_argument_group('Optional arguments:')
opt.add_argument('-l','--locusid', action="store", dest="locusid", help='Locus ID attribute in information column [default: gene_id]', default='gene_id', metavar='')
opt.add_argument('-r','--transid', action="store", dest="transid", help='Transcript ID attribute in information column [default: transcript_id]', default='transcript_id', metavar='')
opt.add_argument('-f','--feature', action="store", dest="feature", help='Annotation feature of interest [default: exon]', default='exon', metavar='')
opt.add_argument('-t','--filetype', action="store", dest="filetype", help='Override file ext and specify type (gff/gtf)', choices=['gff', 'gtf'], metavar='')
opt.add_argument("-h", "--help", action="help", help="show this help message and exit")
args = parser.parse_args()

#############
# FUNCTIONS #
#############

##########
# SCRIPT #
##########

#Determine whether the input file is GFF or GTF from the file extension or -t/--type
if args.filetype is None:
	filename_split = args.gff.split('.')
	filename_split[-1] = filename_split[-1].lower()
	if filename_split[-1] == 'gff' or filename_split[-1] == 'gff3':
		filetype = 'gff'
	elif filename_split[-1] == 'gtf':
		filetype = 'gtf'
	else:
		print 'Extension (' + str(filename_split[-1]) + ') is unrecognized.'
		print 'Please specify annotation type (gff/gtf) with -t/--type\n'
		sys.exit(1) 
else:
	filetype = args.filetype

#Set up the dictionaries for the features we're interested in
locus_dict = {}	#Store genes and their transcripts
trans_dict = {}	#Store transcripts and their lengths
startstop_dict = {}	#Store exon boundaries for total lengths
ori_dict = {}	#Store locus orientations
chr_dict = {}	#Store locus chromosomes

#Now go through the GFF/GTF and concatenate the approporiate info
gff_file = open(args.gff, 'r')
for line in gff_file:
	#Skip commented lines
	if re.match('^#', line):
		continue

	line = line.rstrip('\n')
	line_t = line.split('\t')

	if line_t[2] != args.feature:	#Skip line if it's not the feature type of interest.
		continue

	line_t8 = line_t[8].split(';')

	good = 0 	#Does the line meet the required arguments?

	#Here's what we do if it's a GFF file:
	if filetype == 'gff':
		#Check for custom identifier and determine filetype:
		transcript = None #Reinitialize transcripts.
		if args.locusid + '=' in line_t[8]:	#GFF
			good = 1
			for i in line_t8:
				i.strip()
				if args.locusid + '=' in i:
					i2 = i.split('=')
					name = i2[1]
				if args.transid + '=' in i:
					i2 = i.split('=')
					transcript = i2[1]
		# else:
		# 	print 'Locus ID attribute "' + args.locusid + '" doesn\'t exist or GFF file not properly formatted.' 
		# 	print 'GFF info column format is: attribute=value;'
		# 	sys.exit(1)  

	#Here's what we do if it's a GFF file:
	if filetype == 'gtf':

		if args.locusid + ' ' in line_t[8]: #GTF
			good = 1
			for i in line_t8:
				i.strip()
				if args.locusid + ' ' in i:
					i2 = i.split('=')
					name = i2[1]
				if args.transid + ' ' in i:
					i2 = i.split('=')
					transcript = i2[1]

		# else:
		# 	print 'Locus ID attribute "' + args.locusid + '" doesn\'t exist or GTF file not properly formatted.' 
		# 	print 'GTF info column format is: attribute "value";'
		# 	sys.exit(1)  

	#If the feature was found, add all of the info to the dicts
	if good == 1:
		#Add to locus_dict	
		if name in locus_dict:
			if transcript is not None:
				if transcript not in locus_dict[name]:
					locus_dict[name].append(transcript)
		else:
			locus_dict[name] = []
			if transcript is not None:
				locus_dict[name].append(transcript)

		#Add to trans_dict
		if transcript is not None:
			if transcript in trans_dict:
				trans_dict[transcript] += (int(line_t[4]) - int(line_t[3]) + 1)
			else:
				trans_dict[transcript] = 0
				trans_dict[transcript] += (int(line_t[4]) - int(line_t[3]) + 1)

		#Add to startstop_dict
		if name in startstop_dict:
			startstop_dict[name].append(line_t[3])
			startstop_dict[name].append(line_t[4])
		else:
			startstop_dict[name] = []
			startstop_dict[name].append(line_t[3])
			startstop_dict[name].append(line_t[4])
	
		#Add to ori_dict and chr_dict
		ori_dict[name] = line_t[6]
		chr_dict[name] = line_t[0]
			
gff_file.close()

#Now create the info file
out_file = open(args.outfile, 'w')
out_file.write('LOCUS\tCHR\tORI\tSTART\tSTOP\tNUM_TRANSCRIPTS\tLONGEST_TRANSCRIPT\tLONGEST_TRANSCRIPT_LENGTH\tTRANSCRIPTS\n')

keys = sorted(locus_dict.keys())
for key in keys:
	#Determine the start/stop position of the locus
	start = 'NA'
	stop = 'NA'
	if key in startstop_dict:
		startstop_dict[key].sort()
		start = startstop_dict[key][0]
		stop = startstop_dict[key][-1]
	else:
		print 'NO ' + key + 'IN startstop_dict!!!!'

	#Determine the number of transcripts
	num_trans = len(locus_dict[key])
	
	#Determine the longest transcript
	longest = []
	length = 0
	for trans in locus_dict[key]:
		if trans_dict[trans] > length:
			longest = []
			longest.append(trans)
			length = trans_dict[trans]
		elif trans_dict[trans] == length:
			longest.append(trans)

	if len(longest) > 1:		
		longest_trans = '|'.join(longest)
	else:
		longest_trans = longest[0]

	if len(locus_dict[key]) > 1:
		gene_transcripts = '|'.join(locus_dict[key])
	else:
		gene_transcripts = locus_dict[key][0]

	out_file.write(str(key) + '\t' + str(chr_dict[key]) + '\t' + str(ori_dict[key]) + '\t' + str(start) + '\t' + str(stop)  + '\t' + str(num_trans) + '\t' + str(longest_trans) + '\t' + str(length) + '\t' + gene_transcripts + '\n')
out_file.close()




