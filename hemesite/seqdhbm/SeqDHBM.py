
# coding: utf-8

# # Imports

# In[1]:


#/usr/bin/env python
# Import Modules and Clear the windows command prompt screen
import sys
import time
import datetime
import os
import os.path
import pathlib
import shutil
from prettytable import PrettyTable
import logging
from seqdhbm import fasta
from seqdhbm.SeqResult import SeqResult
import re
from django.conf import settings

start = time.time()  # Program start time


def CalcExecTime(start):
    """ """
    # logging.info("\n")
    # logging.info("*" * 80)
    end = round((time.time() - start), 2)
    # logging.info("Execution time: "+ str(end)+ " seconds")
    # logging.info("*" * 80)


def ReadFasta(filename):
    """1.Read the contents from the fasta file
    2.Count the number of headers
    3.logging.info the number of sequences
    4.Store the header and sequence in a dictionary as key value pairs
    5.Return the dictionary"""
    fasta_dict = {}                           # Initialize an empty dictionary
    content_list = []                         # Read the entire content of the file into this list
    header_list = []                          # Initialize an empty list to collect the headers in the file
    header_index_list = []                    # Initialize an empty list to collect the indices headers in the file
    sequence_list = []                        # Initialize an empty list to collect the contents under each header
    with open(filename, 'r') as infile:
        for line in infile:
            line = line.rstrip()
            if line:                       # To avoid empty lines from being added to the list
                content_list.append(line)  # populate the list, each line from the fastafile is each element of the list
    counter = 0  # Counter to spot header indices since list.index() function does not work like in version 2.7
    for element in content_list:
        counter += 1
        if element[0] == ">":                           # Spot header lines
            header_index = counter - 1                  # Stores the index of the headers
            header_list.append(content_list[header_index])  # populate the header list
            header_index_list.append(header_index)

    for i in range(len(header_index_list)):  # Iterate through the no. of headers i.e. the no. of sequences
        if i != len(header_index_list)-1:  # Check that we are not at the last header yet
            startval = header_index_list[i]+1  # Starting of list range
            endval = header_index_list[i+1]  # Ending of list range
            sequence_element = "".join(content_list[startval:endval])  # Join the lines between startval and endval
            sequence_list.append(sequence_element)  # each element is an individual sequence

        if i == len(header_index_list)-1:  # For the last iteration
            startval = header_index_list[i]+1
            endval = len(content_list)+1
            sequence_element = "".join(content_list[startval:endval])
            sequence_list.append(sequence_element)

            """ Header and sequence list created """
            """ Now store header and sequence as key value pairs in the fasta_dict {} """
    key = 0
    for header in header_list:
        fasta_dict[header] = sequence_list[key]
        key += 1
    # logging.info("--------------------------")
    # logging.info("INPUT FILE CONTENT SUMMARY:")
    # logging.info("--------------------------")
    # logging.info("NOTE : Your input file contains "+str(len(header_list))+" sequence(s)")
    return fasta_dict

# # Program functions

# In[4]:


#######################################################################################################################
################################################
#           Function: SequenceValidityCheck()
################################################
#   1.Take a list of characters and check if each element in the list is part of the 20 standard amino acids
#   2.Return a flag value based on the number of errors in the input
#   3.If all characters are valid then the flag should be 0 and 0 is returned
##################################################
def SequenceValidityCheck(current_sequence_list):
    """Takes a list of characters and checks if each element in the list is part of the 20 standard amino acids

    Return a flag value based on the number of errors in the input
    If all characters are valid then the flag should be 0 and 0 is returned
    """
    standard_aa_list = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L',
                        'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y'] # List of the 20 standard amino acids
    flag = 0
    for i in range(len(current_sequence_list)):
        if current_sequence_list[i] not in standard_aa_list:
            flag += 1
    return flag


#######################################################################################################################
################################################
#           Function: register_complete_result()
################################################
#   Handles all the messages generated by the app execution.
#   Should save into a file and print for the standard output
##################################################
def mylog(lvl, buffer, line):
    """Gets a line of a message. Log it and save into a variable.
    """
    # FOR MORE OUTPUT IN DJANGO CONSOLE, UNCOMMENT THE LINE BELLOW
    # logging.log(lvl, line)
    buffer += [line]


#######################################################################################################################
################################################
#           Function: BuildNinemerSlice()
################################################
#   1.Take a sequence as string and a index value to indicate the coordinating amino acid as int
#   2.Check if the index is within 3 amino acids from either of the terminals
#   3.If found in the terminals add apporiate number of amino acids on the opposite sides to form the 9mer
#   4.Return the 9 mer as string
##################################################
def BuildNinemerSlice(seq,ind):
    """Takes a sequence as string and an index value to indicate the coordinating amino acid as int

    Return the 9 mer as string"""

    # get the 4 aa before the coordinating. If at the beginning of the seq, add '_'
    ninemer = seq[max(ind-4,0):ind].rjust(4, "_") + seq[ind:ind+5].ljust(5, "_")

    assert len(ninemer) == 9, "The ninemer could not be built properly"
    return ninemer


#######################################################################################################################
################################################
#           Function: CheckBasicAdjacent()
################################################
#   1.Take a string of characters which is the 9mer as input
#   2.Check if there are basic amino acids in the 9mer other than the coodrinating AA
#   3.Return success or failure
##################################################
def CheckBasicAdjacent(ninemer_sequence):
    basic_aa_list = ['R', 'K', 'H']  # List of basic and positively charged amino acids
    flag = "n"
    for i in range(len(ninemer_sequence)):
        if i != 4:  # Skip iterating on the coordinating AA in the sequence
            if ninemer_sequence[i] in basic_aa_list:
                flag = "y"
                return flag
    return flag


def CheckCPMotif(ninemer):
    """Checks if the ninemer is coordinated by CP motif.

    Returns Boolean"""
    return (ninemer[4:6] == "CP")  # or ("PC" in ninemer_sequence)


#######################################################################################################################
################################################
#           Function: CheckNetCharge()
################################################
#   1.Take a string of characters which is the 9mer as input
#   2.Compute the net charge on the motif
#   3.Return success or failure
##################################################
def CheckNetCharge(ninemer_sequence):
    basic_aa_list = ['R', 'K', 'H']  # List of basic and positively charged amino acids
    neg_aa_list = ['D', 'E']  # List of negatively charged amino acids
    net_charge = 0
    for i in range(len(ninemer_sequence)):
        if ninemer_sequence[i] in basic_aa_list:
            net_charge += 1
        if ninemer_sequence[i] in neg_aa_list:
            net_charge -= 1
    return net_charge


def ShipSeqToWESA2(seq, seq_pk):
    """Simply ships the sequence to wesa using an standardized jobname."""

    wesa_dir = os.path.join(settings.BASE_DIR, "wesa")
    inp_file = os.path.join(wesa_dir, f"seq_for_wesa{seq_pk}.txt")
    with open(inp_file, 'w') as f:  # Open a text file named seq_for_wesa.txt and write the sequence into it
        f.write(seq)
    jobname = f"SeqDHBM2WESA{seq_pk}"
    email = "seqdhbm@gmail.com"
    html = os.path.join(wesa_dir, jobname+'.html')
    # wesa_tup='python2 WESA-submit.py',jobname, email, inp_file, '>', html # This is stored as a tuple
    wesa_tup = ['python2 ',
                os.path.join(wesa_dir, 'WESA-submit.py'),
                jobname,
                email,
                inp_file,
                '>',
                html
                ]  # This is stored as a tuple
    wesa_str = ' '.join(wesa_tup)  # Convert the list to string
    os.system(wesa_str)  # Send the job to the WESA server


def GetResultsFromWESA(seq_pk):
    """ Checks the WESA server if the results are ready.

    Returns A list with the position of each aa, when ready
            Otherwise returns false  """

    wesa_dir=os.path.join(settings.BASE_DIR, "wesa")
    jobname=f"SeqDHBM2WESA{seq_pk}"
    html=os.path.join(wesa_dir, jobname+'.html')
    download = os.path.join(wesa_dir, jobname+'.out')
    wesa_wget_tup='wget -O', download, '-F -i', html
    wesa_wget_str=' '.join(wesa_wget_tup)  # Convert the tpule to string
    os.system(wesa_wget_str)  # Download the output as a .out file
    time.sleep(1)
    with open(download) as f:
        lines = f.read()
    if "Index of /wesa/out/" in lines:
        return False
    elif ("Job done" in lines) or ("Online version of the prediction is" in lines):
        pass
    else:
        logging.error("The WESA Team might have changed the content of the results")
        logging.error(f"Check the file SeqDHBM2WESA{seq_pk}.out" +
                      " and adapt the program.")
        return False
    # Split in lines and remove leading and trailing spaces
    lines = [x.strip() for x in lines.splitlines()]
    # find the lines containing surface accessibility information
    regex = re.compile("^([0-9]+)+ [A-Z] ")
    # boolean dictionary about surface accessibility info
    exposed_aa = dict()
    for line in lines:
        match = regex.search(line)
        if match:
            exposed_aa[int(match.group(1))] = (line[-7:-6] == '1')
    return exposed_aa


################################################
#           Function: BuildWESANinemerSlice()
################################################
#   1.Take a sequence as string and a index value to indicate the coordinating amino acid as int
#   2.Check if the index is within 3 amino acids from either of the terminals
#   3.If found in the terminals add apporiate number of amino acids on the opposite sides to form the 9mer
#   4.Return the 9 mer as string
##################################################
def ShipSeqToWESA(seq, coord_list):
    basepath = os.path.dirname(os.path.realpath(__file__))
    wesa_tmpdir = os.path.join(basepath, 'WESA_tmp')

    if os.path.exists(wesa_tmpdir):
        shutil.rmtree(wesa_tmpdir)  # Delete previously created WESA_tmp directory and all its contents
    if not os.path.exists(wesa_tmpdir):
        os.makedirs(wesa_tmpdir)
        shutil.copy2('WESA-submit.py', wesa_tmpdir)  # Copy this script into the WESA_tmp directory
        shutil.copy2('MultipartPostHandler.py', wesa_tmpdir)  # Copy this library into the WESA_tmp directory
        if os.path.isfile('wget.exe'):
            shutil.copy2('wget.exe', wesa_tmpdir)  # Copy wget command into the tmp directory for windows
        os.chdir(wesa_tmpdir)
        with open('seq_for_wesa.txt', 'w') as f:
            f.write(seq)
        jobname = "SeqDHBM2WESA"
        email = "seqdhbm@gmail.com"
        inp_file = "seq_for_wesa.txt"
        html = jobname+'.html'
        wesa_tup = 'python2 WESA-submit.py', jobname, email, inp_file, '>', html  # This is stored as a tuple
        wesa_str = ' '.join(wesa_tup) # Convert the tpule to string
        os.system(wesa_str)  # Send the job to the WESA server
        out_list = ""
        wesa_wget_tup = 'wget -O', jobname + '.out', '-F -i', html
        wesa_wget_str = ' '.join(wesa_wget_tup)  # Convert the tpule to string
        os.system(wesa_wget_str)  # Download the output as a .out file
        file_size = os.stat(wesa_wget_tup[1])  # contains the file size of the output file
        initial_file_size = file_size.st_size
        # logging.info("*"*80)
        # logging.info("NOTE : Your sequence has been posted to the WESA server for solvent accessibility prediction")
        # logging.info("NOTE : This might take a few minutes....grab a coffee maybe?")
        # logging.info("NOTE : Making attempts at 30 second intervals to see if the WESA prediction is complete")
        # logging.info("*"*80)
        final_file_size = 0
        attempt_count = 0
        while initial_file_size >= final_file_size:
            attempt_count += 1
            # logging.info("NOTE : Attempt " + str(attempt_count)+" to fetch WESA output...")
            # logging.info("*"*80)
            time.sleep(30)
            os.system(wesa_wget_str)  # Download and overwrite the .out file
            time.sleep(2)
            f_size = os.stat(wesa_wget_tup[1])
            final_file_size = f_size.st_size
        # logging.info("*"*80)
        # logging.info("NOTE : WESA solvent accessibility prediction complete !")
        # logging.info("*"*80)

        with open('SeqDHBM2WESA.out', 'r') as f:  # Read the contents of the output file from WESA
            line_list = []
            out_list = []
            for line in f:
                line = line.lstrip()  # Strip spaces from either side
                line = line.rstrip()
                line_list.append(line)
            for i in range(len(coord_list)):
                for j in range(len(line_list)):
                    if line_list[j].startswith(str(coord_list[i])+' '):
                        out_list.append(line_list[j][-7:-6])
        os.chdir("..")
    return out_list


def coordination_site_check(seq):
    """Write when you can"""
    pass


def disulfide_bond_check(ninemer, cys_cnt):
    """Checks if the ninemer contains a non-coordinating Cys a.a. and there is another Cys in the protein"""
    return "Possible S-S Bond" if (cys_cnt > 1 and ("C" in ninemer[:4]+ninemer[5:])) else " "*17


#######################################################################################################################
################################################
#           Function: SpotCoordinationSite()
#######################################################################################################################
#   1.Take the dictionary fasta_dict from the ReadFasta() function
#   2.Check sequence validity by checking if they are alphabets from the set of the one letter codes of the
#   20 standard amino acids via SequenceValidityCheck()
#   3.Take the first record and logging.infothe number of coordination sites found
#   4.logging.infothe number of C, H and Y and their position in the sequence
#   5.Build the 9mer motif for each coordination site via BuildNinemerSlice()
#   5.For each 9mer motif check(a) Adjacent basic amino acids via CheckBasicAdjacent()
#                              (b) Net charge in the 9mer motif via CheckNetCharge()
#######################################################################################################################
def SpotCoordinationSite(fasta_dict, seq_id, mode):
    scriptname = "SeqD-HBM Online Service"

    filtered_dict = {}  # Empty dictionary that will contain only valid sequences
    invalid_seq_dict = {}  # Empty dictionary to collect all invalid sequence headers
    sno = 0
    MAX_SEQ_LENGTH_FOR_WESA = 2000
    usrout = []

    output = {}
    """ the results of the check. Key is the fasta header and the values are another
         dictionary with:
         results:{coordinating_atom: {ninemer, netcharge, spacercheck}
         warnings: []
         analysis ""
         fail: true/false
         } """

    ###############################
    # Check for sequence validity #
    ###############################
    sno = 0
    for header, sequence in fasta_dict.items():  # Iterate through the dictionary
        sno += 1
        current_sequence = sequence
        current_sequence_list = list(current_sequence)  # Split the sequence into a list

        if len(current_sequence) < 9:
            mylog(logging.INFO, usrout, "--------------------------")
            mylog(logging.INFO, usrout, "SEQUENCE VALIDITY CHECK:")
            mylog(logging.INFO, usrout, "--------------------------")
            mylog(logging.INFO, usrout, "The sequence is too short (minimum: 9)")
            mylog(logging.INFO, usrout, "-" * 80)
            output[header] = {"result": {},
                              "analysis": "\n".join(usrout),
                              "fail": True,
                              "mode": mode,
                              "warnings": ["The sequence is too short (minimum: 9 amino acids)"]}
        elif SequenceValidityCheck(current_sequence_list) == 0:  # Pass the list to the SequenceValidityCheck function
            filtered_dict[header] = sequence  # Add only the valid sequences to the new dictionary
        else:
            mylog(logging.INFO, usrout, "--------------------------")
            mylog(logging.INFO, usrout, "SEQUENCE VALIDITY CHECK:")
            mylog(logging.INFO, usrout, "--------------------------")
            mylog(logging.INFO, usrout, "The following sequence(s) contains invalid characters other " +
                                        "than the 20 standard amino acids")
            mylog(logging.INFO, usrout, "-" * 80)
            output[header] = {"result": {},
                              "analysis": "\n".join(usrout),
                              "fail": True,
                              "mode": mode,
                              "warnings": ["The sequence contains invalid characters " +
                                           "other than the 20 standard amino acids"]}

    if len(fasta_dict) == len(filtered_dict):
        pass  # mylog(logging.INFO, usrout, "NOTE : The sequence were verified to be valid !")
    else:
        for header, sequence in fasta_dict.items():
            if header not in filtered_dict:
                mylog(logging.INFO, usrout, "%s\n%s" % (header[1:], "\n".join(fasta.break_fasta_sequence(sequence))))

    if len(filtered_dict) == 0:  # if this dictionary is empty, all sequences have errors and the program must exit
        for header in fasta_dict:
            output[header]["analysis"] = "\n".join(usrout)
        return output

    #################################
    # Work with the valid sequences #
    #################################
    coordination_site_count = 0
    seq_with_coord = 0
    sno = 0
    for header, current_sequence in filtered_dict.items():  # Iterate through the dictionary
        initial_NinemerDict = {}  # An empty dictionary that will contain the residue number
        # and the associated 9 mer as key value pair eg. {H150: 'XXXXHXXXX'}
        # acid(C or H or Y)
        basic_adj_list = []  # Initialize an empty list to collect the flags when the check for basic adjacent
        # amoni acids is done. Values will be either yes or no.
        dict_for_netCharge_calc = {}  # 9mer motifs that PASS the basic adjacency test are populated here
        pass_charge_dict = {}  # contains 9 mers that have passed the net positive charge check
        pass_charge_index_list = []  # This list contains the indices of the coordination sites after
        # the charge check is done
        spacer_dict = {}  # Dict containing "y" or "n" values to check if two coordination sites are
        # separated by a spacer of at least 2
        pass_charge_out_dict = {}
        # 1102 convert to dict
        # for comparison with the WESA output
        out_coord_atoms = {}  # The output of the function for the current sequence
        # output2[header] = SeqResult(current_sequence, mode)
        output[header] = {
            "warnings": [],
            "result": {},
            "analysis": "",
            "mode": mode,
            "fail": False}  # initialize the informative dictionary
        sno += 1

        ###############################
        # Check for coodinating sites #
        ###############################
        mylog(logging.INFO, usrout, "-" * 80)
        mylog(logging.INFO, usrout, "WORKING ON THE VALID SEQUENCE: "+header[1:])
        mylog(logging.INFO, usrout, "-" * 80)
        mylog(logging.INFO, usrout, "\n".join(fasta.break_fasta_sequence(current_sequence)))
        mylog(logging.INFO, usrout, "-" * 30)
        mylog(logging.INFO, usrout, "HEME COORDINATION SITE CHECK:")
        mylog(logging.INFO, usrout, "-" * 30)

        current_sequence_length = len(current_sequence)
        cys_count = current_sequence.count('C')
        his_count = current_sequence.count('H')
        tyr_count = current_sequence.count('Y')
        coordination_site_count = cys_count + his_count + tyr_count

        if coordination_site_count > 0:
            seq_with_coord += 1
            mylog(logging.INFO, usrout, "NOTE : Heme coordination check PASS!")
            mylog(logging.INFO, usrout, "Length of sequence: "+ str(current_sequence_length))
            mylog(logging.INFO, usrout, f"Total number of potential coordination " +
            f"sites found: {coordination_site_count}")
            mylog(logging.INFO, usrout, "Number of potential CYS based sites: "+str(cys_count))
            mylog(logging.INFO, usrout, "Number of potential HIS based sites: "+str(his_count))
            mylog(logging.INFO, usrout, "Number of potential TYR based sites: "+str(tyr_count)+"\n")

            coord_site_index_list = ([pos for pos, char in enumerate(current_sequence)
                                      if char in('H', 'C', 'Y')])  # List with the indices of the coordination sites
            for i, pos in enumerate(coord_site_index_list):  # Iterate through the list containing the
                # indices of the coordination sites
                pos_on_sequence = pos + 1  # Position on the sequence = index + 1 since Python index starts at 0
                coord_aa = current_sequence[pos]  # Variable stores the value on the index
                # which is the actual amino acid residue
                formatted_coord_site = coord_aa+str(pos_on_sequence)  # Variable stores the amino acid
                # and index in the format eg. H151
                ninemer = BuildNinemerSlice(current_sequence, pos)  # Call the BuildNinemerSlice function
                initial_NinemerDict[formatted_coord_site] = ninemer  # Populate the initial_NinemerDict {}
                # in the format eg. {H12: XXXXHXXXX}

            if i == len(initial_NinemerDict)-1:  # Final record of the initial_NinemerDict{}
                mylog(logging.INFO, usrout, "NOTE : Successfully built 9mer motifs for all the " +
                      str(coordination_site_count) + " potential coordination sites !")
                mylog(logging.INFO, usrout, "-" * 50)


            #######################
            # Check for CP motifs #
            #######################

            cp_motif = {}  # This dictionary will skip basic adjacency
            for aa, ninemer in initial_NinemerDict.items():
                # check if the coordinating aa is Cysteine
                if aa[0] == 'C':
                    pos = int(aa[1:])-1 # the position on string
                    dict_for_netCharge_calc[aa] = ninemer
                    # If it is a CP motif, also store in a dictionary
                    if pos<len(current_sequence)-1 and current_sequence[pos+1]=='P':
                        cp_motif[aa] = ninemer

            ###############################
            # Check for basic amino acids #
            ###############################
            mylog(logging.INFO, usrout, "ADJACENT BASIC AMINO ACID CHECK:")
            mylog(logging.INFO, usrout, "-" * 35)
            mylog(logging.INFO, usrout, "NOTE : Screening all potential motifs for adjacent basic amino acids")

            for key, ninemer in initial_NinemerDict.items():
                basic_adj_list.append(CheckBasicAdjacent(ninemer)) # this list contains values "y" or "n"
                if CheckBasicAdjacent(ninemer) == "y":
                    dict_for_netCharge_calc[key] = ninemer

            count_basic_adj_ninemer = (basic_adj_list.count("y"))

            if count_basic_adj_ninemer > 0:
                mylog(logging.INFO, usrout, "NOTE : %d out of the %d 9mers PASS the adjacent basic amino acids check" %
                      (count_basic_adj_ninemer, coordination_site_count))
                if len(dict_for_netCharge_calc)-count_basic_adj_ninemer:
                    mylog(logging.INFO,
                          usrout,
                          "NOTE : An additional %d " % (len(dict_for_netCharge_calc) - count_basic_adj_ninemer) +
                          "motif coordinated by Cystein will be checked for charge")
                mylog(logging.INFO, usrout, "NOTE : These %d " % len(dict_for_netCharge_calc) +
                                            "9mers will be used in the next step to check for positive net charge")
            elif dict_for_netCharge_calc:
                mylog(logging.INFO, usrout, "NOTE : None of the %d " % coordination_site_count +
                                            "9mers passed the adjacent basic amino acids check")
                mylog(logging.INFO, usrout, "NOTE : %d 9mers coordinated by Cysteine " % len(dict_for_netCharge_calc) +
                                            "will be used in the next step to check for net charge")
            else:
                mylog(logging.INFO, usrout, "-" * 50)
                mylog(logging.INFO, usrout, "NOTE : None of the 9mers have valid motifs")
                mylog(logging.INFO, usrout, "NOTE : The likelyhood of any part of this sequence binding" +
                                            " or coordinating heme is very low !!!")
                mylog(logging.INFO, usrout, "NOTE : Checking the next valid sequence")
                output[header]["warnings"] += ["None of the 9mers have valid motifs.",
                                               "The likelihood of any part of this sequence binding" +
                                               " or coordinating heme is very low"]
                output[header]["fail"] = False
                mylog(logging.INFO, usrout, "-" * 50)
                mylog(logging.INFO, usrout, "-" * 50)
                continue

            ####################
            # NET CHARGE CHECK #
            ####################
            mylog(logging.INFO, usrout, "-" * 35)
            mylog(logging.INFO, usrout, "NET CHARGE CHECK:")
            mylog(logging.INFO, usrout, "-" * 35)
            mylog(logging.INFO, usrout, "NOTE : Checking net charge on the individual 9mer motifs")
            mylog(logging.INFO, usrout, "NOTE : An individual motif PASSES this check:")
            mylog(logging.INFO, usrout, "       if it's net charge is positive")
            mylog(logging.INFO, usrout, "       if it's neutral, but it is a CYS BASED motif")
            mylog(logging.INFO, usrout, "       It's a CP coordinated motif")
            for d in dict_for_netCharge_calc:
                charge = CheckNetCharge(dict_for_netCharge_calc[d])
                if charge > 0:
                    pass_charge_dict[d] = dict_for_netCharge_calc[d]
                    pass_charge_out_dict[d] = "+"+str(charge)
                    #1102 convert to dict
                elif charge == 0 and d[0]=="C":
                    pass_charge_dict[d] = dict_for_netCharge_calc[d]
                    pass_charge_out_dict[d] = str(charge)+"(CYS motif)"
                    #1102 convert to dict
                elif d in cp_motif:
                    pass_charge_dict[d] = dict_for_netCharge_calc[d]
                    pass_charge_out_dict[d] = str(charge)+"(CP motif)"
                    #1102 convert to dict

            mylog(
                logging.INFO,
                usrout,
                (f"NOTE : {len(pass_charge_dict)} out of " +
                 f"{len(dict_for_netCharge_calc)} PASS the net charge check!")
            )
            #Additional coordination site check
            mylog(logging.INFO, usrout, "-" * 50)
            mylog(logging.INFO, usrout, "ADDITIONAL COORDINATION SITE CHECK")
            mylog(logging.INFO, usrout, "-" * 50)
            mylog(
                logging.INFO,
                usrout,
                "NOTE : Checking the presence of additional coordination sites"
            )
            if len(pass_charge_dict) > 1:
                mylog(logging.INFO, usrout, "NOTE : Additional coordination site check: PASS")
                mylog(logging.INFO, usrout, "NOTE : Proceeding to check spacer length between coordination sites")
            elif len(pass_charge_dict) == 1:
                mylog(logging.INFO, usrout, "NOTE : No additional coordination sites found !")
                mylog(logging.INFO, usrout, "NOTE : Spacer check will be skipped !")
            else:
                mylog(logging.INFO, usrout, "NOTE : No coordination sites passed the net charge check !")
                mylog(logging.INFO,
                      usrout,
                      "NOTE : It is very likely that this sequence does not bind/coordinate heme !")
                output[header]["warnings"] += [
                    "No coordination sites passed the net charge check.",
                    "It is very likely that this sequence does not bind/coordinate heme"
                ]
                continue

            ###################
            # Spacer distance #
            ###################
            # logging.info("-" * 50)
            # logging.info("SPACER DISTANCE CHECK")
            # logging.info("-" * 50)
            for head in pass_charge_dict: # Iterate through this dictionary
                # append to the pass_charge_index_list only the number from the
                # dictionary header eg. in C9 extract 9 and converts it to 'int'
                pass_charge_index_list.append(int(head[1:]))
            pass_charge_index_list.sort()
            if (len(pass_charge_index_list) > 1):
                for i in range(len(pass_charge_index_list)):
                    if (i == 0):
                        if abs((pass_charge_index_list[i] - pass_charge_index_list[i+1])) > 2:
                            spacer_dict[pass_charge_index_list[i]] = "YES"
                        else:
                            spacer_dict[pass_charge_index_list[i]] = "NO"
                    elif i == len(pass_charge_index_list)-1:
                        if (abs(pass_charge_index_list[i] - pass_charge_index_list[i-1])) > 2:
                            spacer_dict[pass_charge_index_list[i]] = "YES"
                        else:
                            spacer_dict[pass_charge_index_list[i]] = "NO"
                    else:
                        if ((abs(pass_charge_index_list[i] - pass_charge_index_list[i+1])) > 2 and
                           (abs(pass_charge_index_list[i] - pass_charge_index_list[i-1])) > 2):
                            spacer_dict[pass_charge_index_list[i]] = "YES"
                        else:
                            spacer_dict[pass_charge_index_list[i]] = "NO"
            else:
                spacer_dict[int(pass_charge_index_list[0])] = "NO"  # position of the only valid aa in the chain is NO
            spacer_check_pass = list(spacer_dict.values()).count("YES")

            ##########################
            # WESA (in)compatibility #
            ##########################
            # WESA supports only sequences with length up to 2000
            if (mode == "wesa") and (current_sequence_length > MAX_SEQ_LENGTH_FOR_WESA):
                # output2[header].set_mode("structure")
                mylog(logging.WARNING, usrout, "-" * 50)
                mylog(logging.WARNING, usrout, "Warning:")
                mylog(
                    logging.WARNING,
                    usrout,
                    "Structure prediction by the WESA server"
                    + " supports sequences with length up to"
                    + f" {MAX_SEQ_LENGTH_FOR_WESA} amino acids"
                    )
                mylog(
                    logging.WARNING,
                    usrout,
                    f"The current sequence has {current_sequence_length} a.a."
                    + " and is not supported."
                    )
                output[header]["warnings"] += [
                    "Structure prediction by the WESA server supports sequences with" +
                    " length up to %d amino acids\n" % MAX_SEQ_LENGTH_FOR_WESA
                    ]
                output[header]["warnings"] += [
                    f"This sequence has {current_sequence_length} a.a. " +
                    "and is not supported."
                    ]
                output[header]["mode"] = "structure"

            ##########################
            # WESA is not being used #
            ##########################
            if (mode == "structure") or (current_sequence_length > MAX_SEQ_LENGTH_FOR_WESA):
                # All checks done, preparing tabular summary
                """Prepare output lists for PrettyTable"""
                mylog(logging.INFO, usrout, "*" * 80)
                mylog(logging.INFO, usrout, "TABULAR SUMMARY")
                mylog(logging.INFO, usrout, "NOTE : Please use the available structure "
                                            "information to only consider those motifs that are \"surface exposed\"")
                # table = PrettyTable(["S.no", "Coord. residue", "9mer motif", "Net charge", "Spacer>2", "Binding"])
                table = PrettyTable(["S.no", "Coord. residue", "9mer motif", "Net charge", "Comment", "Kd or strength"])
                sr_no = 0
                output[header]["result"] = {}
                for coord in sorted(pass_charge_dict.keys(), key=lambda x: int(x[1:])):
                    output[header]["result"][coord] = {"ninemer": pass_charge_dict[coord],
                                                       "netcharge": pass_charge_out_dict[coord],
                                                       "comment": disulfide_bond_check(pass_charge_dict[coord],
                                                                                       cys_count)}
                    sr_no += 1
                    out_coord_atoms[coord] = spacer_dict[int(coord[1:])]
                    table.add_row([sr_no, coord, pass_charge_dict[coord], pass_charge_out_dict[coord],
                                   disulfide_bond_check(pass_charge_dict[coord], cys_count), ""])
                mylog(logging.INFO, usrout, str(table))
                output[header]["analysis"] += "\n".join(usrout)

            ######################
            # WESA is being used #
            ######################
            if (mode == "wesa") and (current_sequence_length <= MAX_SEQ_LENGTH_FOR_WESA):
                mylog(logging.INFO, usrout, "Sending sequence to the WESA server for solvent accessibility prediction")
                ShipSeqToWESA2(current_sequence, seq_id)
                output[header]["result"] = {}
                for coord in sorted(pass_charge_dict.keys(), key=lambda x: int(x[1:])):
                    output[header]["result"][coord] = {"ninemer": pass_charge_dict[coord],
                                                       "netcharge": pass_charge_out_dict[coord],
                                                       "comment": disulfide_bond_check(pass_charge_dict[coord],
                                                                                       cys_count)}
                    output[header]["analysis"] += "\n".join(usrout)
                # FUTURE: If the sequence was processed by wesa previously,
                #         fetch the results, save again and present to the user
                # BUT!: Might be affected if the HBM detection algorithm changes
                """ Skip from here "
                wesa_return=ShipSeqToWESA(current_sequence,pass_charge_index_list) # Call the function to send the sequence to WESA passing the sequence as argument
                pass_wesa_index_list=[]
                wesa_spacer_dict={}
                counter=0
                for coord in pass_charge_dict:
                    if(wesa_return[counter]=="1"):
                        pass_wesa_index_list.append(int(coord[1:]))
                    counter+=1
                if len(pass_wesa_index_list):
                    if (len(pass_wesa_index_list) > 1):
                        for i in range(len(pass_wesa_index_list)):
                            if(i == 0):
                                if(abs((pass_wesa_index_list[i] - pass_wesa_index_list[i+1])) > 2):
                                    wesa_spacer_dict[pass_wesa_index_list[i]] = "YES"
                                else:
                                    wesa_spacer_dict[pass_wesa_index_list[i]] = "NO"
                            elif(i == len(pass_wesa_index_list)-1):
                                if((abs(pass_wesa_index_list[i] - pass_wesa_index_list[i-1])) > 2):
                                    wesa_spacer_dict[pass_wesa_index_list[i]] = "YES"
                                else:
                                    wesa_spacer_dict[pass_wesa_index_list[i]] = "NO"
                            else:
                                if((abs(pass_wesa_index_list[i] - pass_wesa_index_list[i+1])) > 2 and(abs(pass_wesa_index_list[i] - pass_wesa_index_list[i-1])) > 2):
                                    wesa_spacer_dict[pass_wesa_index_list[i]] = "YES"
                                else:
                                    wesa_spacer_dict[pass_wesa_index_list[i]] = "NO"
                    else:
                        # logging.info("NOTE : Only one 9mer to check meaning only one valid coordination site")
                        # logging.info("NOTE : Spacer check will be skipped")
                        wesa_spacer_dict[pass_wesa_index_list[0]] = "NO" # position of the only valid aa in the chain is NO
                    # table = PrettyTable(["S.no", "Coordinating residue", "9mer motif", "Net charge", "Spacer > 2", "Binding"])
                    table = PrettyTable(["S.no", "Coordinating residue", "9mer motif", "Net charge", "Comment"])
                    sr_no=0
                    counter=0
                    output[header]["result"] = {}
                    for coord in sorted(pass_charge_dict.keys(), key = lambda x: int(x[1:])):
                        output[header]["result"][coord] = { "ninemer":pass_charge_dict[coord],
                                                            "netcharge":pass_charge_out_dict[coord],
                                                            "comment":disulfide_bond_check(pass_charge_dict[coord], cys_count)}

                        if (wesa_return[counter]=="1"):
                            sr_no+= 1
                            table.add_row([sr_no, coord, pass_charge_dict[coord], 
                                           pass_charge_out_dict[coord], # pass_charge_out_list[counter],
                                           disulfide_bond_check(pass_charge_dict[coord], cys_count)])
                            out_coord_atoms[coord] = wesa_spacer_dict[int(coord[1:])]
                        counter+=1
                    mylog(logging.INFO, usrout, str(table))
                    output[header]["analysis"]+= "\n".join(usrout)
                else:
                    mylog(logging.INFO, usrout, "*"*80)
                    mylog(logging.INFO, usrout, "NOTE : YOUR SEQUENCE HAS NO SOLVENT ACCESSIBLE COORDINATION RESIDUES !")
                    output[header]["warnings"] += ["Your sequence has no solvent accessible coordination residues."]
                    mylog(logging.INFO, usrout, "*"*80)
                    " Skip until here """
        else:  # When there are no coordinating sites in the sequence
            if len(filtered_dict) == 1:  # if the file contains only one sequence
                mylog(logging.INFO, usrout, "-" * 80)
                mylog(logging.INFO,
                      usrout,
                      "NOTE : The sequence does not have potential heme coordination sites(C, H, Y) !!")
                mylog(logging.INFO,
                      usrout,
                      "NOTE : It is very likely that this sequence does not bind/coordinate heme !")
                # mylog(logging.INFO, usrout, "NOTE : This is the only sequence on the file...nothing more to check !")
                output[header]["warnings"] += ["The sequence does not have potential heme coordination sites(C, H, Y) "]
                output[header]["warnings"] += ["It is very likely that this sequence does not bind/coordinate heme"]
                return output
            else:  # When the file contains more than one sequence and we are now at the last sequence
                if sno == len(filtered_dict):
                    mylog(logging.INFO, usrout, "-" * 80)
                    mylog(logging.INFO,
                          usrout,
                          "NOTE : It is very likely that this sequence does not bind/coordinate heme !")
                    mylog(logging.INFO, usrout,
                          "NOTE : The sequence does not have potential heme coordination sites(C, H, Y) !!")
                    # mylog(logging.INFO, usrout, "NOTE : This is the last sequence on the file...nothing more to check !!")
                    output[header]["warnings"] += ["The sequence does not have potential heme" +
                                                   " coordination sites(C, H, Y) "]
                    output[header]["warnings"] += ["It is very likely that this sequence does not bind/coordinate heme"]
                    return output
                mylog(logging.INFO, usrout, "-" * 80) # Any sequence before the last sequence
                mylog(logging.INFO, usrout, "NOTE : It is very likely that this sequence does not bind/coordinate heme")
                mylog(logging.INFO, usrout, "NOTE : The sequence does not have potential heme " +
                                            "coordination sites(C, H, Y), checking the next valid sequence !")
                # logging.info("NOTE : Nothing more to check..moving to the next valid sequece !!")
                output[header]["warnings"] += ["The sequence does not have potential heme coordination sites(C, H, Y) "]
                output[header]["warnings"] += ["It is very likely that this sequence does not bind/coordinate heme"]
                mylog(logging.INFO, usrout, "-" * 80)
    return output
