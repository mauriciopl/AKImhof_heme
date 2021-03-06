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
start = time.time() # Program start time 
os.system('cls')
os.system('clear')

################################################
#           Function: CalcExecTime()
################################################
#   1.Function to calculate the execution time at whatever point it is called
#   2.print the difference between the current time and the value at the 'start' variable at line 5
################################################
def CalcExecTime(start):
	""" """
	print("\n")
	print("*" * 80)
	end = round((time.time() - start),2)
	print("Execution time:", end, "seconds")
	print("*" * 80)


##################################################
scriptname = os.path.basename(__file__)
print('*'*80)
print(scriptname,"v0.9")
print("SeqD-HBM : [Seq]uence based [D]etection of [H]eme [B]inding [M]otifs")
print(datetime.datetime.today().strftime("%A , %B-%d-%Y, %H:%M:%S"))
print('*'*80)
#################################################
if (len(sys.argv)<3 or (sys.argv[2] not in ["default","structure"])):
	print("TOO FEW or INCORRECT command line arguments !")
	print("The program needs 2 command line arguments as follows")
	print("python",scriptname,"Argument1 Argument2")
	print("Where..")
	print("Argument1 : Input file name with the full file extension")
	print("Argument2 : Operation mode, either \"default\" or \"structure\"")
	print("Please try again !")
	CalcExecTime(start)
	sys.exit()
#File Path
input_file_path = os.path.dirname(os.path.realpath(__file__))
print(input_file_path)
input_file_name=sys.argv[1]
operation_mode=sys.argv[2]

if(os.path.isfile(os.path.join(input_file_path,input_file_name))): #Check if the file exists
    fo=open(os.path.join(input_file_path,input_file_name),'r') #Open file in Read mode
    print("NOTE : Your input file is:",input_file_name)
else:
    print("\nINPUT FILE MISSING ! EXITING NOW !")
    CalcExecTime(start)
    sys.exit()

################################################
#           Function: ReadFasta()
################################################
#   1.Read the contents from the opened fasta file
#   2.Count the number of headers
#   3.print the number of sequences
#   4.Store the header and sequence in a dictionary as key value pairs
#   5.Return the dictionary
##################################################
def ReadFasta(infile):
    """ """
    fasta_dict={}                           # Initialize an empty dictionary
    content_list=[]                         # Read the entire content of the file into this list
    header_list=[]                          # Initialize an empty list to collect the headers in the file
    header_index_list=[]                    # Initialize an empty list to collect the indices headers in the file
    sequence_list=[]                        # Initialize an empty list to collect the contents under each header
    for line in infile:
        line = line.rstrip()
        if line != '':                      # To avoid empty lines from being added to the list
            content_list.append(line)       # populate the list, each line from the fasta file is each element of the list
    infile.close()          # Since the contents of the file have been read into content_list, close the file.
    counter = 0             # Initialize a counter to spot header indices since list.index() function does not work like in version 2.7
    for element in content_list:
        counter += 1
        if element[0] == ">":                           # Spot header lines 
            header_index = counter - 1                  # Stores the index of the headers 
            header_list.append(content_list[header_index]) # populate the header list
            header_index_list.append(header_index)
    
    for i in range(len(header_index_list)): # Iterate through the no. of headers i.e. the no. of sequences
        if i !=(len(header_index_list)-1):  # Check that we are not at the last header yet
            startval = header_index_list[i]+1 # Starting of list range 
            endval = header_index_list[i+1] # Ending of list range
            sequence_element =("".join(content_list[startval:endval])) # Join the lines between startval and endval
            sequence_list.append(sequence_element) # each element is an individual sequence
        
        if i ==(len(header_index_list)-1): # For the last iteration
            startval = header_index_list[i]+1
            endval = len(content_list)+1
            sequence_element =("".join(content_list[startval:endval]))
            sequence_list.append(sequence_element)
        
            """ Header and sequence list created """
            """ Now store header and sequence as key value pairs in the fasta_dict {} """
    key = 0
    for header in header_list:
        fasta_dict[header] = sequence_list[key] 
        key += 1
    print("--------------------------")
    print("INPUT FILE CONTENT SUMMARY:")
    print("--------------------------")
    print("NOTE : Your input file contains",len(header_list),"sequence(s)")
    return(fasta_dict) 
############################################################################################################################################
################################################
#           Function: SpotCoordinationSite()
#############################################################################################################################################################
#   1.Take the dictionary fasta_dict from the ReadFasta() function
#   2.Check sequence validity by checking if they are alphabets from the set of the one letter codes of the 20 standard amino acids via SequenceValidityCheck()
#   3.Take the first record and printthe number of coordination sites found 
#   4.printthe number of C, H and Y and their position in the sequence
#   5.Build the 9mer motif for each coordination site via BuildNinemerSlice()
#   5.For each 9mer motif check(a) Adjacent basic amino acids via CheckBasicAdjacent()
#                              (b) Net charge in the 9mer motif via CheckNetCharge()
##############################################################################################################################################################
def SpotCoordinationSite(fasta_dict):
    filtered_dict = {} # Empty dictionary that will contain only valid sequences
    invalid_seq_dict  = {} # Empty dictionary to collect all invalid seqence headers
    sno = 0
    coordination_site_count = 0
    seq_with_coord = 0
    print("--------------------------")
    print("SEQUENCE VALIDITY CHECK:")
    print("--------------------------")
    for header in fasta_dict: # Iterate through the dictionary
        sno += 1
        current_sequence =(fasta_dict[header])
        current_sequence_list = list(current_sequence) # Split the sequence into a list

        #print("***** Checking sequence",sno,"under header:", header[1:],"*****")
        if(SequenceValidityCheck(current_sequence_list) == 0): # Pass the list to the SequenceValidityCheck function
            #print("NOTE : Sequence content check: SEQUENCE VALID !") # if all sequences have standard amino acids in the sequences then the value will be 0
            filtered_dict[header] = fasta_dict[header] # Add only the valid sequences to the new dictionary
        else:
            invalid_seq_dict[header] = fasta_dict[header]
    if (len(fasta_dict) == len(filtered_dict)):
        print("NOTE : All the",len(fasta_dict),"sequences were verified to be valid !")
    else:
        print("NOTE :",len(filtered_dict),"sequences out of",len(fasta_dict),"are valid")
        print("--------------------")
        print("INVALID SEQUENCE(S)")
        print("--------------------")
        print("NOTE : The following sequence(s) contains invalid characters other than the 20 standard amino acids \n")
        inv=0
        for header in invalid_seq_dict:
            inv += 1
            print(inv,".",header) 

    if(len(filtered_dict) == 0): # if this dictionary is empty, then all sequences have errors and the program must exit
        print("NOTE : ALL SEQUENCES IN YOUR FILE CONTAIN ONE OR MORE INVALID CHARACTERS !!")
        print("NOTE : PLEASE CHECK YOUR INPUT SEQUENCE(S) AND TRY AGAIN !")
        print("NOTE : PROGRAM WILL EXIT NOW !")
        CalcExecTime(start)
        sys.exit()

    #print("-" * 80) 
    #print("NOTE : The valid sequences will now be screened for the potential heme coordination sites(C, H, Y)")
    #print("-" * 80)
    sno = 0 
    for header in filtered_dict: # Iterate through the dictionary
        initial_NinemerDict = {} # An empty dictionary that will contain the residue number and the associated 9 mer as key value pair eg. {H150: 'XXXXHXXXX'}
        dict_index_site = {} # Dictionary that stores the index of a possible coordination site and the amino acid(C or H or Y)
        coordination_site_count = 0 # This counter is used later to determine if the program must end
        basic_adj_list = [] # Initialize an empty list to collect the flags when the check for basic adjacent amoni acids is done. Values will be either yes or no.
        net_charge_list = [] # Initialize a list to store the net charges computed by the CheckNetCharge() function
        pos_charge_list = [] # list with the index of 9mers with positive net charge
        dict_for_netCharge_calc = {} # 9mer motifs that PASS the basic adjacency test are populated here
        neg_charge_list =[]
        pos_check_lst = []
        pass_charge_dict = {} # contains 9 mers that have passed the net positive charge check
        pass_charge_index_list = [] # This list contains the indices of the coordination sites after the charge check is done
        spacer_list = [] # List containing "y" or "n" values to check if two coordination sites are separated by a spacer of at least 2 
        count_basic_adj_ninemer = 0 # Initialize the count of basic adjacent AAs in each ninemer
        pass_charge_out_list = []
        wesa_substr_index_list = [] # List containing indices of the starting positions of the 9mers for comparison with the WESA output
        cys_count = 0
        his_count = 0
        tyr_count = 0
        sno += 1
        current_sequence =(filtered_dict[header])
        #print("\n")
        print("-" * 80)
        print("-" * 80)
        print("WORKING ON THE VALID SEQUENCE",sno,".",header[1:]) 
        print("-" * 80)
        print(current_sequence)
        print("-" * 30)
        print("HEME COORDINATION SITE CHECK:")
        print("-" * 30)
        
        current_sequence_length = len(current_sequence)
        cys_count = current_sequence.count('C')
        his_count = current_sequence.count('H')
        tyr_count = current_sequence.count('Y')
        coordination_site_count = cys_count + his_count  + tyr_count
    
        if(coordination_site_count > 0 ):
            seq_with_coord += 1
            print("NOTE : Heme coordination check PASS!")
            print("Length of sequence:", current_sequence_length)
            print("Total number of potential coordination sites found: ",coordination_site_count)
            print("Number of potential CYS based sites:",cys_count)
            print("Number of potential HIS based sites:",his_count)
            print("Number of potential TYR based sites:",tyr_count,"\n")
            
            coord_site_index_list =([pos for pos, char in enumerate(current_sequence) if char in('H','C','Y')]) # List with the indices of the coordination sites
            for i in range(len(coord_site_index_list)): # Iterate through the list containing the indices of the coordination sites
                pos_on_sequence = coord_site_index_list[i] + 1 # Position on the sequence = index + 1 since Python index starts at 0
                coord_aa = current_sequence[coord_site_index_list[i]] # Variable stores the value on the index which is the actual amino acid residue
                formatted_coord_site =(coord_aa+str(pos_on_sequence)) # Variable stores the amino acid and index in the format eg. H151
                ninemer = BuildNinemerSlice(current_sequence,coord_site_index_list[i]) # Call the BuildNinemerSlice function
                initial_NinemerDict[formatted_coord_site] = ninemer # Populate the initial_NinemerDict {} in the format eg. {H12: XXXXHXXXX}

            if(i ==(len(initial_NinemerDict)-1)): # Final record of the initial_NinemerDict{}
                print("NOTE : Successfully built 9mer motifs for all the ",coordination_site_count,"potential coordination sites !")
                print("-" * 50)

            print("ADJACENT BASIC AMINO ACID CHECK:")
            print("-" * 35)
            print("NOTE : Screening all potential motifs for adjacent basic amino acids")
            
            for y in initial_NinemerDict:
                basic_adj_list.append((CheckBasicAdjacent(initial_NinemerDict[y]))) # this list contains values "y" and "n"
                if((CheckBasicAdjacent(initial_NinemerDict[y])) == "y"):
                    dict_for_netCharge_calc[y] = initial_NinemerDict[y]
            count_basic_adj_ninemer =(basic_adj_list.count("y"))

            if(count_basic_adj_ninemer > 0):
                print("NOTE :",count_basic_adj_ninemer,"out of the",coordination_site_count,"9mers PASS the adjacent basic amino acids check")
                print("NOTE : These",count_basic_adj_ninemer,"9mers will be used in the next step to check for positive net charge")

            if(count_basic_adj_ninemer == 0): # If all elements in the list are "n" this means that none of the 9mers have adjacent basic amino acids 
                print("-" * 50)
                print("NOTE : None of the 9mers have adjacent basic amino acids")
                print("NOTE : This also means that none of these 9mer motifs will have a net positive charge")
                print("NOTE : The likelyhood of any part of this sequence binding or coordinating heme is very low !!!")
                print("NOTE : Checking the next valid sequence")
                print("-" * 50)
                print("-" * 50)
                continue
            
            #NET CHARGE CHECK
            print("-" * 35)
            print("NET CHARGE CHECK:")
            print("-" * 35)
            print("NOTE : Checking net charge on the individual 9mer motifs")
            print("NOTE : An individual motif PASSES this check if its net charge is positive")
            print("NOTE : An individual motif also PASSES this check if its net charge is NOT positive BUT it is a CYS BASED motif")
            #print("-" * 50)
            for z in dict_for_netCharge_calc:
                net_charge_list.append(CheckNetCharge(dict_for_netCharge_calc[z]))
            nt_cg_counter = 0 # counter to loop into the net_charge_list
            for d in dict_for_netCharge_calc:
                if(net_charge_list[nt_cg_counter] > 0 ):
                    pass_charge_dict[d] = dict_for_netCharge_calc[d]
                    #print("Motif",d,"PASSES NET CHARGE CHECK: REASON - Positive net charge:",net_charge_list[nt_cg_counter])
                    pass_charge_out_list.append(net_charge_list[nt_cg_counter])
                else:
                    if(net_charge_list[nt_cg_counter] <= 0 and d[0]=="C"):
                        pass_charge_dict[d] = dict_for_netCharge_calc[d]
                        #print("Motif",d,"PASSES NET CHARGE CHECK: REASON - CYS based motif")
                        pass_charge_out_list.append (str(net_charge_list[nt_cg_counter])+"(CYS motif)")
                nt_cg_counter += 1
            print("NOTE :",len(pass_charge_dict),"out of",count_basic_adj_ninemer,"PASS the net charge check!")
            #Additional coordination site check
            print("-" * 50)
            print("ADDITIONAL COORDINATION SITE CHECK")
            print("-" * 50)
            print("NOTE : Checking the presence of additional coordination sites")
            if(len(pass_charge_dict) > 1):
                print("NOTE : Additional coordination site check: PASS")
                print("NOTE : Proceeding to check spacer length between coordination sites")
            if(len(pass_charge_dict) == 1):
                print("NOTE : No additional coordination sites found !")
                print("NOTE : Spacer check will be skipped !")

            #print("\n")
            print("-" * 50)
            print("SPACER DISTANCE CHECK")
            print("-" * 50)
            for head in pass_charge_dict: # Iterate through this dictionary
                pass_charge_index_list.append(int(head[1:])) # append to the pass_charge_index_list only the number from the dictionary header eg. in C23 extract 23 and convert it to 'int'
            if (len(pass_charge_index_list) > 1):
                for i in range(len(pass_charge_index_list)):
                    if(i == 0):
                        if(abs((pass_charge_index_list[i] - pass_charge_index_list[i+1])) > 2): 
                            spacer_list.append("YES")
                        else:
                            spacer_list.append("NO")
                    if(i > 0 and i <(len(pass_charge_index_list)-1)):
                        if((abs(pass_charge_index_list[i] - pass_charge_index_list[i+1])) > 2 and(abs(pass_charge_index_list[i] - pass_charge_index_list[i-1])) > 2):
                            spacer_list.append("YES")
                        else:
                            spacer_list.append("NO")
                    if(i == len(pass_charge_index_list)-1):
                        if((abs(pass_charge_index_list[i] - pass_charge_index_list[i-1])) > 2):
                            spacer_list.append("YES")
                        else:
                            spacer_list.append("NO")
            else:
                print("NOTE : Only one 9mer to check meaning only one valid coordination site")
                print("NOTE : Spacer check will be skipped")
                spacer_list.append("NO")
            spacer_check_pass = spacer_list.count("YES")
            print("NOTE :",spacer_check_pass, "out of", len(pass_charge_index_list), "PASS the spacer check!")
            if (sys.argv[2]=="structure"):
                print("NOTE : All checks done, preparing tabular summary")
                """Prepare output lists for PrettyTable"""
                print("*" * 110)
                print("TABULAR SUMMARY")
                print("NOTE : Please use the available structure information to only consider those motifs that are \"surface exposed\"")
                print("*" * 110)
                table = PrettyTable(["S.no", "Coordinating residue", "9mer motif", "Net charge", "Spacer > 2"])
                sr_no = 0
                for header in pass_charge_dict:
                    sr_no+= 1
                    table.add_row([sr_no, header, pass_charge_dict[header], pass_charge_out_list[sr_no-1], spacer_list[sr_no-1]])
                print(table)
                print(len(pass_charge_dict),len(pass_charge_out_list),len(spacer_list))

            if (sys.argv[2]=="default"):
                print("Sending sequence to the WESA server for solvent accessibility prediction")
                wesa_return=ShipSeqToWESA(current_sequence,pass_charge_index_list) # Call the function to send the sequence to WESA passing the sequence as argument
                pass_wesa_index_list=[]
                wesa_spacer_list=[]
                counter=0
                for header in pass_charge_dict:
                    if(wesa_return[counter]=="1"):
                        pass_wesa_index_list.append(int(header[1:]))
                    counter+=1
                if (len(pass_wesa_index_list) > 1):
                    for i in range(len(pass_wesa_index_list)):
                        if(i == 0):
                            if(abs((pass_wesa_index_list[i] - pass_wesa_index_list[i+1])) > 2): 
                                wesa_spacer_list.append("YES")
                            else:
                                wesa_spacer_list.append("NO")
                        if(i > 0 and i <(len(pass_wesa_index_list)-1)):
                            if((abs(pass_wesa_index_list[i] - pass_wesa_index_list[i+1])) > 2 and(abs(pass_wesa_index_list[i] - pass_wesa_index_list[i-1])) > 2):
                                wesa_spacer_list.append("YES")
                            else:
                                wesa_spacer_list.append("NO")
                        if(i == len(pass_wesa_index_list)-1):
                            if((abs(pass_wesa_index_list[i] - pass_wesa_index_list[i-1])) > 2):
                                wesa_spacer_list.append("YES")
                            else:
                                wesa_spacer_list.append("NO")
                else:
                    print("NOTE : Only one 9mer to check meaning only one valid coordination site")
                    print("NOTE : Spacer check will be skipped")
                    wesa_spacer_list.append("NO")
                table = PrettyTable(["S.no", "Coordinating residue", "9mer motif", "Net charge", "Spacer > 2"])
                sr_no=0
                counter=0
                for header in pass_charge_dict:
                    if(wesa_return[counter]=="1"):
                        sr_no+= 1
                        table.add_row([sr_no, header, pass_charge_dict[header], pass_charge_out_list[counter], wesa_spacer_list[sr_no-1]])
                    counter+=1
                if (sr_no>0):
                    print(table)
                else:
                    print("*"*80)
                    print("NOTE : YOUR SEQUENCE HAS NO SOLVENT ACCESSIBLE COORDINATION RESIDUES !")
                    print("*"*80)
        else: # When the number of coordination sites in the sequence is 0
            if(len(filtered_dict) == 1): # if the file contains only one sequence
                print("-" * 80)
                print("NOTE : The sequence does not have potential heme coordination sites(C, H, Y) !!")
                print("NOTE : It is very likely that this sequence does not bind/coordinate heme !")
                print("NOTE : This is the only sequence on the file...nothing more to check !")
                print("-" * 80)
                print("PROGRAM WILL EXIT NOW !!")
                CalcExecTime(start)
                sys.exit()
            else: # When the file contains more than one sequence and we are now at the last sequence
                if(sno == len(filtered_dict)):
                    print("-" * 80)
                    print("NOTE : It is very likely that this sequence does not bind/coordinate heme !")
                    print("NOTE : The sequence does not have potential heme coordination sites(C, H, Y) !!")
                    print("NOTE : This is the last sequence on the file...nothing more to check !!")
                    print("-" * 80)
                    print("PROGRAM WILL EXIT NOW !!")
                    CalcExecTime(start)
                    sys.exit()
                print("-" * 80) # Any sequence before the last sequence
                print("NOTE : It is very likely that this sequence does not bind/coordinate heme")
                print("NOTE : The sequence does not have potential heme coordination sites(C, H, Y), checking the next valid sequence !")
                print("NOTE : Nothing more to check..moving to the next valid sequece !!")
                print("-" * 80)


#################################################################################################################################################
################################################
#           Function: SequenceValidityCheck()
################################################
#   1.Take a list of characters and check if each element in the list is part of the 20 standard amino acids
#   2.Return a flag value based on the number of errors in the input
#   3.If all characters are valid then the flag should be 0 and 0 is returned
##################################################          
def SequenceValidityCheck(current_sequence_list):
    standard_aa_list = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y'] # List of the 20 standard amino acids
    flag = 0
    for i in range(len(current_sequence_list)):
        if current_sequence_list[i] not in standard_aa_list:
            flag +=1
    return(flag)


################################################################################################################################
################################################
#           Function: BuildNinemerSlice()
################################################
#   1.Take a sequence as string and a index value to indicate the coordinating amino acid as int
#   2.Check if the index is within 3 amino acids from either of the terminals
#   3.If found in the terminals add apporiate number of amino acids on the opposite sides to form the 9mer 
#   4.Return the 9 mer as string
##################################################          
def BuildNinemerSlice(seq,ind):
    seq_length = len(seq)
    """When the coordinating residue is found in the first 5 residues of the sequence"""
    if(ind <= 4): # When the coordinating residue is found in the first 5 residues of the sequence
        ninemer = seq[0:9] # String slice of the first 9 AAs of the sequence
        return(ninemer)
    """When the coordinating residue is found in the last 5 residues of the sequence"""
    if(ind >= seq_length-5): # When the coordinating residue is found in the last 5 residues of the sequence
        ninemer = seq[seq_length-9:seq_length] # String slice of the last 9 AAs of the sequence
        return(ninemer)
    if(ind >= 5 and ind < seq_length-5): # When the coordinating residue is in between and outside the above two conditions
        ninemer = seq[ind-4:ind+5] # String slice of the last 4 AAs from either side of the coord AA
        return(ninemer)


##############################################################################################################################
################################################
#           Function: CheckBasicAdjacent()
################################################
#   1.Take a string of characters which is the 9mer as input
#   2.Check if there are basic amino acids in the 9mer other than the coodrinating AA
#   3.Return success or failure 
##################################################
def CheckBasicAdjacent(ninemer_sequence):
    basic_aa_list = ['R', 'K', 'H'] # List of basic and positively charged amino acids
    flag = "n"
    for i in range(len(ninemer_sequence)):
        if(i != 4): # Skip iterating on the coordinating AA in the sequence
            if(ninemer_sequence[i] in basic_aa_list):
                flag = "y"
                return(flag)
    return(flag)


##############################################################################################################################
################################################
#           Function: CheckNetCharge()
################################################
#   1.Take a string of characters which is the 9mer as input
#   2.Compute the net charge on the motif
#   3.Return success or failure
##################################################
def CheckNetCharge(ninemer_sequence):
    basic_aa_list = ['R', 'K', 'H'] # List of basic and positively charged amino acids
    neg_aa_list = ['D','E'] # List of negatively charged amino acids
    net_charge = 0
    for i in range(len(ninemer_sequence)):
        if(ninemer_sequence[i] in basic_aa_list):
            net_charge += 1
        if(ninemer_sequence[i] in neg_aa_list):
            net_charge -= 1
    return(net_charge)

################################################
#           Function: BuildWESANinemerSlice()
################################################
#   1.Take a sequence as string and a index value to indicate the coordinating amino acid as int
#   2.Check if the index is within 3 amino acids from either of the terminals
#   3.If found in the terminals add apporiate number of amino acids on the opposite sides to form the 9mer 
#   4.Return the 9 mer as string
##################################################          
def ShipSeqToWESA(seq,coord_list):
    basepath=os.path.dirname(os.path.realpath(__file__))
    wesa_tmpdir=os.path.join(basepath,'WESA_tmp')
    
    if os.path.exists(wesa_tmpdir):
        shutil.rmtree(wesa_tmpdir) # Delete previously created WESA_tmp directory and all its contents 

    if not os.path.exists(wesa_tmpdir):
        os.makedirs(wesa_tmpdir)
        shutil.copy2('WESA-submit.py',wesa_tmpdir) # Copy this script into the WESA_tmp directory
        shutil.copy2('MultipartPostHandler.py',wesa_tmpdir) # Copy this library into the WESA_tmp directory
        if os.path.isfile('wget.exe'):
            shutil.copy2('wget.exe',wesa_tmpdir) # Copy wget command into the tmp directory for windows
        os.chdir(wesa_tmpdir)
        f=open('seq_for_wesa.txt', 'w') # Open a text file named seq_for_wesa.txt and write the sequence into it
        f.write(seq)
        f.close()
        jobname="SeqDHBM2WESA"
        email="mauriciopl@gmail.com"
        inp_file="seq_for_wesa.txt"
        html=jobname+'.html'
        wesa_tup='python2 WESA-submit.py',jobname, email, inp_file, '>', html # This is stored as a tuple
        wesa_str=' '.join(wesa_tup) # Convert the tpule to string
        #print(wesa_str)
        os.system(wesa_str) # Send the job to the WESA server
        wesa_wget_tup='wget -O',jobname+'.out', '-F -i', html
        wesa_wget_str=' '.join(wesa_wget_tup) # Convert the tpule to string
        #print(wesa_wget_tup[1])
        os.system(wesa_wget_str) # Download the output as a .out file
        file_size=os.stat(wesa_wget_tup[1]) # contains the file size of the output file
        initial_file_size=file_size.st_size
        print("*"*80)
        print("NOTE : Your sequence has been posted to the WESA server for solvent accessibility prediction")
        print("NOTE : This might take a few minutes....grab a coffee maybe?")
        print("NOTE : Making attempts at 30 second intervals to see if the WESA prediction is complete")
        print("*"*80)
        final_file_size=0
        attempt_count=0
        while (initial_file_size>=final_file_size):
            attempt_count+=1
            print("*"*80)
            print("NOTE : Attempt",attempt_count,"to fetch WESA output...")
            print("*"*80)
            time.sleep(30)
            os.system(wesa_wget_str) # Download and overwrite the .out file
            time.sleep(2)
            f_size=os.stat(wesa_wget_tup[1])
            final_file_size=f_size.st_size
        print("*"*80)
        print("NOTE : WESA solvent accessibility prediction complete !")
        print("*"*80)

        f=open('SeqDHBM2WESA.out', 'r') # Read the contents of the output file from WESA
        line_list=[]
        out_list=[]
        for line in f:
            line = line.lstrip() # Strip spaces from either side 
            line = line.rstrip()
            line_list.append(line)
        for i in range(len(coord_list)):
            for j in range(len(line_list)):
                if (line_list[j].startswith(str(coord_list[i])+' ')): 
                    out_list.append(line_list[j][-7:-6])
        f.close()

    return(out_list)
##############################################################################################################################
##############################################################################################################################
#Function Calls
SpotCoordinationSite(ReadFasta(fo))
CalcExecTime(start)
##############################################################################################################################
