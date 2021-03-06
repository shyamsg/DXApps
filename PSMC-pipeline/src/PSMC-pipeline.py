#!/usr/bin/env python
# PSMC-pipeline 0.0.1
# Generated by dx-app-wizard.
#
# Basic execution pattern: Your app will run on a single machine from
# beginning to end.
#
# See http://wiki.dnanexus.com/Developer-Portal for documentation and
# tutorials on how to modify this file.
#
# DNAnexus Python Bindings (dxpy) documentation:
#   http://autodoc.dnanexus.com/bindings/python/current/

import os
import dxpy
import sys
import subprocess
import re
from math import ceil, floor
import gzip
import pickle
import numpy as np

MINPOS = 2700025
LINEWD = 60
PROBPICK = '/usr/data/problemSites.pck'

def loadSeq(filename):
    """This loades the sequence from the consensus file.
    """
    f = gzip.open(filename, 'rb')
    reached = False
    for line in f:
        line = line.strip()
        if line == '': continue
        if line[0] == '>':
            curPos = int(line[1:])
            if (curPos + LINEWD) > MINPOS:
                reached = True
                continue
        elif reached:
            print filename, line
            f.seek((MINPOS-curPos-LINEWD-1),os.SEEK_CUR)
            break
        else: continue
    seq = ''
    for line in f:
        line = line.strip()
        if (line == ''): continue
        if line[0] == '>': continue
        seq += line
    f.close()
    return (MINPOS, seq)

def windowElement(s1, s2, mp):
    """This computes the window element 
    given the 2 seqs and the prop of missing
    tolerated
    """
    missLim = floor(mp*len(s1))
    bases = ['A', 'C', 'G', 'T']
    for i, j in zip(s1, s2):
        if (i not in bases or j not in bases):
            missLim -= 1
            if (missLim < 0):
                return 'N'
        elif i != j:
            return 'K'
    return 'T'

def createPSMCfa(file1, file2, outname, skip):
    """This function creates the psmcfa file
    locally.
    """
    # Fill in your application code here.
    (st1, seq1) = loadSeq(file1)
    print 'Loaded sequence 1'
    (st2, seq2) = loadSeq(file2)
    print 'Loaded sequence 2'
    print outname
    
    miss = 0.05
    thisStart = st1
    if(st1 < st2):
        seq1 = seq1[(st2-st1):]
        thisStart = st2
    elif (st2 < st1):
        seq2 = seq2[(st1-st2):]
        thisStart = st1

    thisEnd = thisStart
    if (len(seq2) > len(seq1)):
        seq2 = seq2[0:len(seq1)]
        thisEnd += len(seq1)
    elif (len(seq1) > len(seq2)):
        seq1 = seq1[0:len(seq2)]
        thisEnd += len(seq2)
    else:
        thisEnd += len(seq1)

    pf = open(PROBPICK)
    probsites = pickle.load(pf)
    pf.close()
    probsites = np.array(probsites)
    rara = np.sum(probsites > thisEnd)
    if rara > 0:
        probsites = probsites[np.sum(probsites<thisStart):-rara]
    else:
        probsites = probsites[np.sum(probsites<thisStart):]
    probsites = probsites - thisStart
    probsites = probsites[0:np.sum(probsites < len(seq1))]
    print 'Done loading probsites'
    sys.stdout.flush()
    seq1 = np.array(list(seq1))
    print 'Converted seq1 to array'
    sys.stdout.flush()
    seq2 = np.array(list(seq2))
    print 'Converted seq2 to array'
    sys.stdout.flush()
    seq1[probsites] = 'N'
    print 'Changed probsites to N seq1'
    sys.stdout.flush()
    seq2[probsites] = 'N'
    print 'Changed probsites to N seq2'
    sys.stdout.flush()
    del probsites
#    seq1 = ''.join(seq1)
#    print 'Got seq1 back'
#    sys.stdout.flush()
#    seq2 = ''.join(seq2)
#    print 'Got seq2 back'
    print 'Done dealing with probsites'
    sys.stdout.flush()

    numWindows = int(ceil((thisEnd - thisStart)/skip))
    numTotWin = int(ceil((155260557-MINPOS)/skip))

    curStart = MINPOS
    faStr = ''
    for i in xrange(numTotWin):
        if curStart < thisStart:
            faStr += 'N'
        elif curStart > thisEnd:
            faStr += 'N'
        else:
            faStr += windowElement(seq1[curStart-thisStart:curStart-thisStart+skip], seq2[curStart-thisStart:curStart-thisStart+skip], miss)
        curStart += skip
        if (curStart % 30000000 == 0):
            print curStart
    linesize = 100
    o = open(outname, 'w')
    o.write('>\n')
    curStart = 0
    while(curStart < len(faStr)):
        o.write(faStr[curStart:curStart+linesize])
        o.write('\n')
        curStart += linesize
    o.close()
    del faStr
    del seq1, seq2
    return

def genTR(fname):
    """This function generates ntot, nfree, pattern and theta/rho 
    vectors.
    """
    nfree = 0
    ntot = 0
    pattern = ''
    thetas = 0
    rhos = 0
    f = os.popen('grep pattern '+fname)
    line = f.readline()
    line = line.strip()
    toks = line.split()
    currpattern = (toks[1].split(':')[1])[0:-1]
    if (pattern == ''):
        pattern = currpattern
    elif (pattern != currpattern):
        raise Exception('Pattern not same for all input files.\n')
    currntot = int((toks[2].split(':')[1])[0:-1])
    if (ntot == 0):
        ntot = currntot
    elif (ntot != currntot):
        raise Exception('Total parameters not same for all input files.\n')
    currnfree = int((toks[3].split(':')[1]))
    if (nfree == 0):
        nfree = currnfree
    elif (nfree != currnfree):
        raise Exception('Free parameters not same for all input files.\n')
    f.close()
    cmd = 'tail -n 2 '+fname+' | head -1'
    f = os.popen(cmd)
    line = f.readline()
    line = line.strip()
    toks = line.split()
    thetas = float(toks[2])
    rhos = float(toks[3])
    currLs = []
    for ll in xrange(nfree):
        currLs.append(float(toks[4+ll]))
    f.close()
    return (pattern, ntot, nfree, thetas, rhos, currLs)

def gettimes(tmax_orig, tmax_new):
    """
    This method returns the time boundaries.
    In this case, it is linear with 5ky lengths
    in the near past and 10ky lengths earlier
    and so on.
    In detail:
    0-100KYA:    20*5KY   -> 20*0.01 = 0.2
    100-250KYA:  15*10KY  -> 15*0.02 = 0.3
    250-500KYA:  10*25KY  -> 10*0.05 = 0.5
    500-1MYA:    5*100KY  -> 5*0.2   = 1
    1MYA-7.5MYA: 13*500KY -> 13*1    = 13
    The final window that exists from 7.5MYA to infinite time back.
    """
    times = np.ones(63)
    times[0:20] = times[0:20]*0.01
    times[20:35] = times[20:35]*0.02
    times[35:45] = times[35:45]*0.05
    times[45:50] = times[45:50]*0.2
    times[50:] = times[50:]*1
    times = times.cumsum()
    times = times*tmax_new/tmax_orig
    return times

def writeRecalFile(fname, maxtime, window, xChr):
    maxtime=7.5e6
    if (xChr):
        mu = 2.2e-8
    else:
        mu = 2.5e-8
    gtime = 25
    tmax_orig = maxtime/(2e4*gtime)
    (pattern, ntot, nfree, thetas, rhos, Ls) = genTR(fname)
    tmaxNew = 4*maxtime*window*mu/(2*gtime*thetas)
    fntemp = fname+'.temp2.pars'
    outf = open(fntemp, 'w')
    outf.write('3*2+52*1+6\n')
    outf.write(str(thetas)+'\n')
    outf.write(str(rhos)+'\n')
    ts = gettimes(tmax_orig, tmaxNew)
    for lllo in range(56):
        outf.write('1.0000\n')
    outf.write('\n'.join([str(x) for x in ts]))
    outf.write('\n')
    outf.close()
    return (tmaxNew, fntemp)

@dxpy.entry_point('main')
def main(cons1, cons2, outroot, xchr=True, recalnums=1, skip=20, timemax=7500000.0):

    # The following line(s) initialize your data object inputs on the platform
    # into dxpy.DXDataObject instances that you can start using immediately.

    cons1 = dxpy.DXFile(cons1)
    cons2 = dxpy.DXFile(cons2)

    # The following line(s) download your file inputs to the local file system
    # using variable names for the filenames.

    dxpy.download_dxfile(cons1.get_id(), "cons1")
    dxpy.download_dxfile(cons2.get_id(), "cons2")
    outname1 = outroot + '.psmcfa'
    outname2 = outroot + '.psmc'

    # Fill in your application code here.
    #create the psmcfa file
    createPSMCfa('cons1', 'cons2', outname1, skip)
    print 'Generated the PSMC fasta file.'
    sys.stdout.flush()
    #run psmc the first time
    subprocess.check_call(['psmc', '-t', '15', '-r', '5', '-p', "4+25*2+4+6", '-o', 'test.psmc', outname1])
    print 'Done with first run of PSMC.'
    sys.stdout.flush()
    #run the recal script and run psmc again.
    while (recalnums > 1):
        (tmaxNew, parfile) = writeRecalFile('test.psmc', timemax, skip, xchr)
        subprocess.check_call(['psmc', '-t', str(round(tmaxNew,4)), '-i', parfile, '-o', 'test.psmc', outname1])
        recalnums -= 1
        print 'Recals left', recalnums
        sys.stdout.flush()
    (tmaxNew, parfile) = writeRecalFile('test.psmc', timemax, skip, xchr)
    subprocess.check_call(['psmc', '-t', str(round(tmaxNew,4)), '-i', parfile, '-o', outname2, outname1])
    print 'Finished final recalibration run.'

    # The following line(s) use the Python bindings to upload your file outputs
    # after you have created them on the local file system.  It assumes that you
    # have used the output field name for the filename for each output, but you
    # can change that behavior to suit your needs.

    outfile1 = dxpy.upload_local_file(outname1);
    outfile2 = dxpy.upload_local_file(outname2);

    # The following line fills in some basic dummy output and assumes
    # that you have created variables to represent your output with
    # the same name as your output fields.
    output = {}
    output["outfile1"] = dxpy.dxlink(outfile1)
    output["outfile2"] = dxpy.dxlink(outfile2)

    return output

dxpy.run()
