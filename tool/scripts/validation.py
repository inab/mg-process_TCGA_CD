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

def validation(inFile,refFile,species='HUMAN',outlog=sys.stdout):
  ## Load proteome file 
  all_proteins = []
  for line in open(refFile, "r"):
    ## Skip header
    if line.find(species) == -1 or line.startswith("#"):
      continue
    ## We save field #2 which contains protein "Entry Name"
    f = [e.strip() for e in line.split("\t")]
    all_proteins.append(f[1])
  print('[1]\t{0:14} => {1:10,g}\n'.format("All Proteins", len(all_proteins)),file=outlog)

  if not all_proteins:
    return "ERROR: Check Reference Proteome File Content '%s'. Tag: [%s]" \
      % (refFile, species)
      
  ## Load file to be validated 
  input_proteins = []
  for line in open(inFile, "r"):
    ## Skip header
    if line.startswith("#"):
      continue
    ## We save field #1 which contains protein "Entry Name"
    f = [e.strip() for e in line.split("\t")]
    input_proteins.append(f[0])
    
  print('[2]\t{0:14} => {1:10,g}\n'.format("Detected Proteins", \
    len(input_proteins)),file=outlog)

  if not input_proteins:
    return "ERROR: Check Input File Content '%s'. Tag: [%s]" % (args.inFile,
      args.species)

  dif = set(input_proteins) - set(all_proteins)
  if dif != set():
    return "ERROR: Some entries (%d|%s) present at the Input File are not " \
      + "part of the Reference Proteome file" % (len(dif), "|".join(dif))

  return True

if __name__ == "__main__":

  parser = argparse.ArgumentParser()

  parser.add_argument("--reference", dest = "refFile", required = True,  type = \
    str, help = "Reference Proteome List")

  parser.add_argument("--species_tag", dest = "species", default = "HUMAN",  
    type = str, help = "Set mnemotechnic UNIPROT species label")

  parser.add_argument("--input", dest = "inFile", required = True, type = str,
    help = "Provide the input file to be validated")

  args = parser.parse_args()

  ## Check reference proteome file
  if not os.path.isfile(args.refFile):
    sys.exit(("ERROR: Check Reference Proteome File '%s'") % (args.refFile))

  ## Check input file to be validated
  if not os.path.isfile(args.inFile):
    sys.exit(("ERROR: Check Input File '%s'") % (args.inFile))

  retval = validation(args.inFile,args.refFile,args.species)
  if retval is not True:
    sys.exit(retval)