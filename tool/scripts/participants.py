#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   [2018] S. Capella-Gutierrez - salvador.capella@bsc.es
#	Some adaptations from José Mª Fernández - jose.m.fernandez@bsc.es
#
#   this script is free software: you can redistribute it and/or modify it under
#   the terms of the GNU General Public License as published by the Free
#   Software Foundation, the last available version.
#
#   this script is distributed in the hope that it will be useful, but WITHOUT
#   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#   FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
#   more details on <http://www.gnu.org/licenses/>
#

from __future__ import print_function

import os
import sys
import random
import hashlib
import argparse


def participants(refFile,species,goldenFiles,repeats,outFolder,outlog=sys.stdout):
  # Assuring the destination directory does exist
  try:
    os.makedirs(outFolder)
  except e:
    pass
  
  ## Load proteome file 
  all_proteins = []
  for line in open(refFile, "r"):
    ## Skip header
    if line.find(species) == -1:
      continue
    ## We save field #2 which contains protein "Entry Name"
    f = [e.strip() for e in line.split("\t")]
    all_proteins.append(f[1])
  print('[1]\t{0:14} => {1:10,g}\n'.format("All Proteins", len(all_proteins)),file=outlog)
  
  remaining_proteins = set(all_proteins)
  gold_datasets = {}
  
  for infile in goldenFiles:
    ref = ".".join(os.path.split(infile)[1].split(".")[:-1])
    
    gold_datasets.setdefault(ref, set())
    for line in open(infile, "r"):
      ## Skip header
      if line.find(species) == -1:
        continue
      ## We save field #1 which contains protein "Entry Name"
      f = [e.strip() for e in line.split("\t")]
      gold_datasets[ref].add(f[0])
      
    remaining_proteins -= gold_datasets[ref]
    print('[2]\t{0:14} => {1:10,g}'.format(ref, len(gold_datasets[ref])),file=outlog)


  print ("",file=outlog)
  ## Execute the following code as many time as input datasets you would like
  ## to generate.
  for n in range(repeats):
    
    sample = set()
    for ref in gold_datasets:
      sample |= set(random.sample(list(gold_datasets[ref]), random.randint(0, 
		len(gold_datasets[ref]))))
        
    true_positive = len(sample)
    false_positive = random.randint(0, len(remaining_proteins))
    sample |= set(random.sample(list(remaining_proteins), false_positive))

    sorted_ids = ",".join(sorted(sample)).encode('utf-8')
    run_id = hashlib.md5(sorted_ids).hexdigest()
    
    print('[3]\tRun: {0:12} => Size: {1:6,g} TP: {2:6,g} FP: {3:,g}'.format( \
       run_id, true_positive + false_positive, true_positive, false_positive),\
       file=outlog)
    
    with open(os.path.join(outFolder,"%s.list" % (run_id)), "w") as outfile:
      outfile.write("\n".join(sorted(sample)))

if __name__ == "__main__":

  parser = argparse.ArgumentParser()

  parser.add_argument("--reference", dest = "refFile", required = True,  type = \
	str, help = "Reference Proteome List")

  parser.add_argument("--species_tag", dest = "species", default = "HUMAN",  
	type = str, help = "Set mnemotechnic UNIPROT species label")

  parser.add_argument("--output_folder", dest = "outFolder", default = os.getcwd(), \
	type = str, help = "Set output folder")

  parser.add_argument("--golden", dest = "goldenFiles", default = [], type = str,
	nargs = "+", help = "Provide at least one golden reference dataset")

  parser.add_argument("--repeats", dest = "repeats", default = 1, type = int,
	help = "Set how many reference datasets you would to generate")

  args = parser.parse_args()

  ## Check reference proteome file
  if not os.path.isfile(args.refFile):
    sys.exit(("ERROR: Check Reference Proteome File '%s'") % (args.refFile))

  ## Check golden dataset files
  goldenFiles = []
  for infile in args.goldenFiles:
    if not os.path.isfile(infile):
      print("ERROR: Check Golden Reference File '%s'" % (infile))
      continue
    goldenFiles.append(infile)

  if not goldenFiles:
    sys.exit(("ERROR: Check provided Golden Reference File/s"))
  
  participants(args.refFile,args.species,goldenFiles,args.repeats,args.outFolder)
