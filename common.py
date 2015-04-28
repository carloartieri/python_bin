####################
# GLOBAL VARIABLES #
####################

#ANSI escape codes corresponding to visible print colors.
ansi_colors = {
    'grey' : '\033[90m',
    'red' : '\033[91m',
    'green' : '\033[98m',
    'blue' : '\033[96m',
    'violet' : '\033[95m',
    'darkblue' : '\033[94m',
    'darkgreen' : '\033[92m',
    'tan' : '\033[93m',
    'white' : '\033[97m',
    'reset' : '\x1b[0m',
    'blink' : '\033[5m', #Just kidding
}

#############
# FUNCTIONS #
#############

#Adds color/bold/underline to the default print command.
#Usage: print_ansi(TEXT, COLOR, BOLD [T/F], UNDERLINE [T/F]):
def print_ansi(text, color, bold=False, under=False):
    if bold == True:
        bold = '\033[1m'
    else:
        bold = ""

    if under == True:
        under = '\033[4m'
    else:
        under = ""

    print(under + bold + ansi_colors[color] + text + '\x1b[0m')
    
    
#Convert a FASTA file to a dictionary where keys = headers and values are the sequence
#Usage: dict = fasta_to_dict(FILE):
def fasta_to_dict(file):

    fasta_file = open(file, "r")    #Open the file for reading
    fasta_dic = {}
    
    for line in fasta_file:
        line = line.rstrip('\n')
        if re.match('^>', line):
            line_split = line.split(' ')    #By default keeps only first word of the header.
            header = line_split[0].translate(None, '>')
            fasta_dic[header] = ''
        else:
            fasta_dic[header] += line   
    
    fasta_file.close()
    
    return fasta_dic

#Splits a CIGAR string into two lists where the one letter type and numerical value are in
#the same order as found in the string.
#Usage: cigar_types,cigar_vals = split_CIGAR(<CIGAR>)
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
	

#Convert a sequence to its reverse-complement. Supports 'N's, which remain 'N's.
#Modified from http://crazyhottommy.blogspot.com/2013/10/python-code-for-getting-reverse.html
#Usage: REVSEQ = ReverseComplement(SEQ)
def ReverseComplement(seq):
    # too lazy to construct the dictionary manually, use a dict comprehension
    seq1 = 'ATCGNTAGCNatcgntagcn'
    seq_dict = { seq1[i]:seq1[i+5] for i in range(20) if i < 5 or 10<=i<15 }
    return "".join([seq_dict[base] for base in reversed(seq)])