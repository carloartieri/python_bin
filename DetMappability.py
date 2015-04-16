#!/usr/bin/python

# Created on: 2015.04.13 
# Author: Carlo Artieri

##############################
# HISTORY AND THINGS TO FIX  #
##############################
#2015.04.13 - Initial script
#			- Non-functional, in planning stages.
#2015.04.14	- Finished preliminary script. Resolve following bugs:
#			  First position in the output file is wrong and has '0' for edit_dist, no NA
#			  Two soft-clips in the same read cause two 'S' in type
#			  Make sure that -c/-clipmax takes into account sum of all clips
#			  Test NM tag on I/D CIGARs to see how edit distance is handled.
#2015.04.15	- Fixed first position error
#			  Fixed clipmax
#			  Added I/D edit distance calc, but still not sure if I/D is included in NM tag,
#			  information I've found seems to suggest no.
#			- Want to output the edit distance in BedGraph format to load onto IGV.

###########
# MODULES #
###########
import sys			#Access to simple command-line arguments
import argparse		#Access to long command-line parsing	
import datetime		#Access to calendar/clock functions
import re			#Access to REGEX splitting
import math			#Access to math functions
import subprocess	#Access to shell commands
import random		#Access to random number generator
import os 			#Access to shell commands

##########################
# COMMAND-LINE ARGUMENTS #
##########################

epilog = """\
This script determines the mappability of reads of a specified length to a specified genome 
using the Burrows-Wheeler Aligner in MEM mode (http://bio-bwa.sourceforge.net/), which must be 
installed and in the PATH.

An input FASTA is tiled into segments of length N, and mapped back to the whole genome, 
recording the minimum 'edit distance' to the original location among all reads that  can be 
mapped elsewhere.

edit distance = # of mismatches + # indel bases + # of soft-clips

Reads that cannot be mapped elsewhere are assigned an edit distance of int(N/2). 

More detailed description of options follows:

-f/--fasta
	An input FASTA file containing the sequences upon which to determine mappability. The 
	script runs in two 'modes'. If the FASTA is the whole genome (or whole chromsomes), 
	mappabiltiy for the whole genome will be reported. If the FASTA contains segments of the
	genome, then a GFF/GTF file MUST be provided with the -g/--gff command giving the genomic
	coordinates of the segments. Each segment must be a single GFF line with a column 9 
	identifier matching the header of the segment in the FASTA (e.g. gene=ADH; for a GFF, 
	gene "ADH"; for a GTF)

-l/--length
	The length of the reads for which to determine mappability.

-o/--outfile
	The name of a table that will contain the following columns:

	CHROMOSOME
	POSITION 	1-based position
	FEATURE 	Name of the feature if running in -g/--gff mode
	MIN_EDIT_DIST 	The minimum edit distance to map non-specifically for this position
	EDIT_TYPE 	The min necessary edits: M, mismatch; I, insertion; D, deletion: S, soft-clip

-x/--index
	Location of the bwa mem index. 

-t/--threads
	Number of CPUs to use for BWA.

-g/--gff
	GFF or GTF annotation file for running the script on genomic segments. See above.

-i/--identifier
	The identifier in column 9 to use for matching the annotations to the FASTA file. In GFF 
	files, this is typically 'gene', whereas in GTF files it's 'gene_id' 

-b/--bedgraph
	In addition to the output table, produce a track of edit distance in BedGraph format
	(see: http://genome.ucsc.edu/goldenpath/help/bedgraph.html)

-c/--clipmax
	The maximum value that soft-clips can contribute to the edit distance. For example, if 
	mapping without allowing clipping, set this to 0.

	
"""
class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(description='Determine the DNA-seq mappability of genomic regions using BWA', add_help=False, epilog=epilog, formatter_class=CustomFormatter)
req = parser.add_argument_group('Required arguments:')
req.add_argument('-f','--fasta', action='store', dest='fasta', help='Input fasta file', required=True, metavar='')
req.add_argument('-l','--length', action='store', dest='length', type=int, help='Length of sequences to determine mappability', required=True, metavar='')
req.add_argument('-o','--outfile', action='store', dest='outfile', help='Output table containing mappability information', required=True, metavar='')
bwa = parser.add_argument_group('bwa-specific arguments:')
bwa.add_argument('-x','--index', action='store', dest='index', help='bwa mem index', default=None, metavar='', required=True,)
bwa.add_argument('-t','--threads', action='store', dest='threads', type=int, help='Number of bwa threads', default='1', metavar='')
opt = parser.add_argument_group('Optional arguments:')
opt.add_argument('-g','--gff', action='store', dest='gff', help='Supply gff and run in feature mode (see below)', metavar='')
opt.add_argument('-i','--identifier', action='store', dest='id', help='GFF/GTF column 9 identifier of interest', default='gene', metavar='')
opt.add_argument('-b','--bedgraph', action='store_true', dest='bg', help='Produce a BedGraph formatted track from the output table named <output>.bg')
opt.add_argument('-c','--clipmax', action='store', dest='clip', help='Max soft-clips to add to edit distance', type=int, default='30', metavar='')
opt.add_argument('-h', '--help', action='help', help='show this help message and exit')

args = parser.parse_args()

#############
# FUNCTIONS #
#############

#Creates a dictionary from a FASTA file where: dict[header] = sequence
def fasta_to_dict(file):

	fasta_file = open(file, "r")	#Open the file for reading
	fasta_dic = {}
	
	for line in fasta_file:
		line = line.rstrip('\n')
		if re.match('^>', line):
			line_split = line.split(' ')	#By default keeps only first word of the header.
			header = line_split[0].translate(None, '>')
			fasta_dic[header] = ''
		else:
			fasta_dic[header] += line	
	
	fasta_file.close()
	
	return fasta_dic

#Splits a CIGAR string into two lists where the one letter type and numerical value are in
#the same order as found in the string.
def split_CIGAR(cigar):

	cig_types_tmp = re.split('[0-9]',cigar)
	cig_vals_tmp = re.split('[MIDNSHP\=X]',cigar)
	cig_types = []
	cig_vals = []

	for i in cig_types_tmp:
		if i != '':
			cig_types.append(i)

	for i in cig_vals_tmp:
		if i != '':
			cig_vals.append(i)
		
	return cig_types,cig_vals


##########
# SCRIPT #
##########

#First step is to read in the FASTA sequence and create the 'dummy' FASTQ
fasta_dict = fasta_to_dict(args.fasta)
out_fastq_name = args.fasta + '.temp.fastq'
out_fastq = open(out_fastq_name, 'w')	#Open a temporary file where we'll hold
													#our dummy FASTQ
#Initialize a mismatch dictionary for plotting purposes.
mismatch_dist = {}
mismatch_min_type = {}

#If we're running in 'feature' mode, then we supply a gff file to determine the actual genomic
#coordinates of the sequences.
if args.gff is not None:
	gff_dict = {}
	gff_file = open(args.gff, 'r')
	for line in gff_file:
		if re.match('^#', line):
			continue

		gff_type = args.id + '='
		gtf_type = args.id + ' "'

		line = line.rstrip('\n')
		line_t = line.split('\t')
		if gff_type in line_t[8]:
				line_t8_split = line_t[8].split(';')
				for i in line_t8_split:
					if gff_type in i:
						type_split = i.split('=')
						start = int(line_t[3])-1
						gff_dict[type_split[1]] = [line_t[0],start]

		elif gtf_type in line_t[8]:
				line_t8_split = line_t[8].split(';')
				for i in line_t8_split:
					if gtf_type in i:
						type_split = i.split('"')
						type_split[1] = type_split[1].strip()
						start = int(line_t[3])-1
						gff_dict[type_split[1]] = [line_t[0],start]
	gff_file.close()

keys = sorted(fasta_dict.keys())
for key in keys:
	seq_len = len(fasta_dict[key])
	mismatch_dist[key] = [0]*seq_len

	#Tile across the sequence with substrings
	for i in range(seq_len):
		#If we're running in feature mode, then we need to adjust the read positions by
		#the gff coordinates. Header will be in format @GENE|CHR|0-START|0-STOP
		if args.gff is not None:
			start = i + int(gff_dict[key][1])
			stop = start + args.length
			chrom = gff_dict[key][0]
		else:
			start = i
			stop = start + args.length
			chrom = key
		i_stop = i + args.length #Set the substr
		
		if i_stop <= seq_len:
			subseq = fasta_dict[key][i:i_stop]
			qual = '~' * args.length #Quality will be max value
			out_fastq.write('@' + str(key)+'|'+str(chrom)+'|'+str(start)+'|'+str(stop-1)+'\n'+subseq+'\n'+'+\n'+qual+'\n')
out_fastq.close()

#Now we map the FASTQ back to the genome using BWA. 
os.system('bwa mem -a -t ' + str(args.threads) + str(args.index) + ' ' + str(out_fastq_name) + '> ' + str(args.fasta) + '.temp.sam')

#Now go through the SAM file and extract mismatching reads.
sam_file = open(args.fasta + '.temp.sam', 'r')
curr_read = None
min_edit_dist = None
edit_dist = None
min_mis_type = None
mis_type = None

#Open the outfile where we'll write our mismatch table
mismatch_table = open(args.outfile, 'w')
mismatch_table.write('CHROMOSOME\tPOSITION\tFEATURE\tMIN_EDIT_DIST\tEDIT_TYPE\n')

for line in sam_file:
	if re.match('^@', line):
		continue

	line = line.rstrip('\n')
	line_t = line.split('\t')

	read_deets = line_t[0].split('|')

	edit_dist = None
	mis_type = []

	#Determine the edit distance, which is the value of soft-clips 'S' in the CIGAR string plus
	#mismatches in the NM flag.
	
	#First soft-clips if they exist
	cigar_types,cigar_vals = split_CIGAR(line_t[5])
	rem_clip = args.clip

	for i in range(len(cigar_types)):
		if cigar_types[i] == 'S':
			mis_type.append(str(cigar_types[i])+cigar_vals[i])

			#Adjust for max clip distance:
			if int(cigar_vals[i]) > rem_clip:
				if edit_dist is None:
					edit_dist = int(rem_clip)
					rem_clip = 0
				else:
					edit_dist += int(rem_clip)
					rem_clip = 0
			else:
				if edit_dist is None:
					edit_dist = int(cigar_vals[i])
					rem_clip -= int(cigar_vals[i])
				else:
					edit_dist += int(cigar_vals[i])
					rem_clip -= int(cigar_vals[i])

		elif cigar_types[i] == 'D':
			mis_type.append(str(cigar_types[i])+cigar_vals[i])
			if edit_dist is None:
					edit_dist = int(cigar_vals[i])
			else:
				edit_dist += int(cigar_vals[i])
		
		elif cigar_types[i] == 'I':
			mis_type.append(str(cigar_types[i])+cigar_vals[i])
			if edit_dist is None:
					edit_dist = int(cigar_vals[i])
			else:
				edit_dist += int(cigar_vals[i])

	#Now NM tags
	tags = line_t[11].split(' ')
	for tag in tags:
		if 'NM' in tag:
			tag_val = tag.split(':')
			if int(tag_val[2]) == 0:
				pass
			else:
				mis_type.append('M'+str(tag_val[2]))
				if edit_dist is None:
					edit_dist = int(tag_val[2])
				else:
					edit_dist += int(tag_val[2])

	if curr_read is None:
		curr_read = line_t[0]
		curr_read_deets = read_deets
		min_edit_dist = None
		if line_t[3] == int(read_deets[2])+1 and line_t[2] == read_deets[1]:
			pass
		else:
			min_edit_dist = edit_dist
			min_mis_type = mis_type

	elif curr_read == line_t[0]:
		curr_read_deets = read_deets
		if line_t[3] == int(read_deets[2])+1 and line_t[2] == read_deets[1]:
			pass
		else:
			#Is the edit-distance less than the minimum edit distance?
			if min_edit_dist is None:
				min_edit_dist = edit_dist
				min_mis_type = mis_type
			elif edit_dist < min_edit_dist:
				min_edit_dist = edit_dist
				min_mis_type = mis_type

	elif curr_read != line_t[0]:

		#Print everything to the table
		if min_edit_dist is None:
			min_edit_dist = int(args.length/2)
			mistype = 'NA'
		else:
			if len(min_mis_type) == 1:
				mistype = min_mis_type[0]
			else:
				mistype = '|'.join(min_mis_type)
		if args.gff is None:
			feat = 'NA'
		else:
			feat = read_deets[0]

		mismatch_table.write(str(curr_read_deets[1]) + '\t' + str(int(curr_read_deets[2])+1) + '\t' + feat + '\t' + str(min_edit_dist) + '\t' + mistype + '\n')

		#Reset everything
		min_edit_dist = None
		edit_dist = None
		min_mis_type = None
		mis_type = None

		#Do analysis with new read
		curr_read = line_t[0]
		curr_read_deets = read_deets
		if line_t[3] == int(read_deets[2])+1 and line_t[2] == read_deets[1]:
			pass
		else:
			min_edit_dist = edit_dist
			min_mis_type = mis_type

#Write out the last line before closing the output file

if min_edit_dist is None:
	min_edit_dist = int(args.length/2)
	mistype = 'NA'
else:
	if len(min_mis_type) == 1:
		mistype = min_mis_type[0]
	else:
		mistype = '|'.join(min_mis_type)
if args.gff is None:
	feat = 'NA'
else:
	feat = read_deets[0]

mismatch_table.write(str(curr_read_deets[1]) + '\t' + str(int(curr_read_deets[2])+1) + '\t' + feat + '\t' + str(min_edit_dist) + '\t' + mistype + '\n')

sam_file.close()
mismatch_table.close()

#Generate BedGraph track if args.bg is True
if args.bg is True:
	outbg_file_name = str(args.outfile) + '.bedgraph'
	outbg_file = open(outbg_file_name, 'w')
	#Track header
	outbg_file.write('track type=bedGraph name='+ str(args.outfile) + ' description=' + str(args.outfile) +' color=0,0,0\n')
	#BedGraph options: track type=bedGraph name=track_label description=center_label
        #visibility=display_mode color=r,g,b altColor=r,g,b
        #priority=priority autoScale=on|off alwaysZero=on|off
        #gridDefault=on|off maxHeightPixels=max:default:min
        #graphType=bar|points viewLimits=lower:upper
        #yLineMark=real-value yLineOnOff=on|off
        #windowingFunction=maximum|mean|minimum smoothingWindow=off|2-16
	
	infile = open(args.outfile, 'r')
	val = None
	curr_chr = None
	start_pos = 0
	for line in infile:
		if re.match('^CHROMOSOME', line):
			continue

		line = line.rstrip('\n')
		line_t = line.split('\t')

		if val is None:
			val = line_t[3]
			curr_chr = line_t[0]
			start_pos = int(line_t[1])-1
			stop_pos = int(line_t[1])-1

		elif val == line_t[3] and curr_chr == line_t[0]:
			stop_pos = int(line_t[1])-1
		else:
			outbg_file.write(str(curr_chr)+'\t'+str(start_pos)+'\t'+str(stop_pos)+'\t'+str(val)+'\n')
			val = line_t[3]
			curr_chr = line_t[0]
			start_pos = int(line_t[1])-1
			stop_pos = int(line_t[1])-1
	outbg_file.close()

