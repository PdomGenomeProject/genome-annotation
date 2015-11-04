#!/usr/bin/env python
import re, sys

if __name__ == "__main__":
  usage = ("\nReplace sequence IDs using the given correspondence of new IDs to old IDs.\n"
           "Usage: python seq-ids.py mapping.txt < seqs.fasta > seqs-fixed.fasta\n")

  if len(sys.argv) != 2:
    print >> sys.stderr, usage

  mapping1 = {}
  mapping2 = {}
  for line in open(sys.argv[1], "r"):
    line = line.rstrip()
    newid, oldid1, oldid2 = line.split("\t")
    mapping1[oldid1] = newid
    mapping2[oldid2] = newid

  for line in sys.stdin:
    line = line.rstrip()
    seqidmatch = re.search("^>(\S+)", line)
    if seqidmatch:
      seqid = seqidmatch.group(1)
      assert seqid in mapping1 or seqid in mapping2, seqid
      if seqid in mapping1:
          newid = mapping1[seqid]
      else:
          newid = mapping2[seqid]
      line = re.sub("^>(\S+)", r">%s \1" % newid, line)
    print line
