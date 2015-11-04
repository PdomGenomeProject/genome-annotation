# Genome annotation

This data set is part of the [*Polistes dominula* genome project][pdomproj], and details the annotation of protein coding genes and tRNA genes in the *P. dominula* genome, as described in (Standage *et al.*, manuscript in preparation).
Included in this data set are the annotations (gene models in GFF3 format), gene model translations (peptide sequences in Fasta format), and documentation providing complete disclosure of the annotation workflow.

## Synopsis

The [Maker annotation pipeline][] version 2.31.6 was used to annotate protein-coding genes and tRNA genes in the *P. dominula* genome.

## Data access

The genome annotation depends on the following data.

- The repeat-masked *Polites dominula* reference genome assembly, available at DOI [10.6084/m9.figshare.1593187](http://dx.doi.org/10.6084/m9.figshare.1593187).
- Alignments of transcripts from 3 *Polistes* species to the *P. dominula* genome, available at DOI [10.6084/m9.figshare.1593326](http://dx.doi.org/10.6084/m9.figshare.1593326).
- Alignments of proteins from the honey bee *Apis mellifera* and the fruit fly *Drosophila melanogaster* to the *P. dominula* genome, available at DOI [10.6084/m9.figshare.1593958](http://dx.doi.org/10.6084/m9.figshare.1593958).

For convenience, the following input data has been included in this data set.

- Gene structures for genes highly conserved in the Hymenoptera (`xxx`).
- Gene structures for manual gene annotations submitted by the research community using PdomGDB's yrGATE community annotation portal (`xxx`).
- HMM parameter filees trained specifically for gene finding in *P. dominula* (`xxx`).

## Procedure

### Gene predictor training

Approximately 3,000 genes were selected from annotations whose reliability was confirmed by strict measures of conservation with several other Hymenopteran species.
These genes were then used to train 3 *ab initio* gene predictors (SNAP, Augustus, and GeneMark) for use with the Maker pipeline.
For Augustus and SNAP, the procedures documented in their respective source code distributions were followed.
For GeneMark, a model built by the self-training version of GeneMark was used with Maker.

### Preliminaries

Here is a list of input files to check for.

```bash
# Masked genome sequence
ls pdom-scaffolds-masked-r1.2.fa

# Transcript alignments
ls pdom-tsa-masked.gff3 pcan-tsa-masked.gff3 pmet-tsa-masked.gff3

# Protein alignments
ls amel-ncbi-prot.gff3 amel-ogs-prot.gff3 dmel-flybase-prot.gff3
```

Augustus requires some configuration to install and find HMM files.

```bash
export AUGUSTUS_CONFIG_DIR=/usr/local/src/augustus/config
tar -xzf pdom.augustus.tar.gz
mv pdom ${AUGUSTUS_CONFIG_DIR}/species
```

### Configuration files

The following command will create the necessary Maker control files.
If all of the supplementary programs are the in the path, the `maker_exe.ctl` file will be populated automatically.
If not, you will need to manually fill it in with the location of all the programs.
Rather than manually editing the `maker_opts.ctl` file, we'll simply copy ours over.

```bash
maker -CTL
cp pdom_maker_opts.ctl maker_opts.ctl
```

### Execute the annotation workflow

After all of the data files and control files are in place, running Maker is trivial.

```bash
NumProcs=16
maker -genome pdom-scaffolds-masked-r1.2.fa \
      -fix_nucleotides \
      -nodatastore \
      -RM_off \
      -cpus $NumProcs \
      -base pdom \
      > pdom.maker.log 2>&1
```

### Post-processing

The feature IDs created internally by Maker are pretty unwieldy, so we use a few scripts to clean them up.

```bash
# Merge and clean up data
gff3_merge -o pdom-annot-p1.2-raw.gff3 pdom.maker.output/pdom_master_datastore_index.log
bash clean.sh pdom-annot-p1.2-raw.gff3 > pdom-annot-p1.2-cleaned.gff3
# Fixes strange output artifact for some VIGA-based predictions
perl -n fix.pl < pdom-annot-p1.2-cleaned.gff3 > pdom-annot-p1.2-fixed.gff3

# Create a polished GFF3 file with official IDs for the annotations and proper
# ##sequence-region pragmas.
gt gff3 -retainids -sort -tidy pdom-annot-p1.2-fixed.gff3 2> gt.log \
    | python annot-ids.py --idfmt='Pdom%sr1.2-%05lu' -n --rnamap=rnaids.txt --dbxref=MAKER - \
    | python fix-regions.py pdom-scaffolds-masked-r1.2.fa > pdom-annot-r1.2.gff3

# Create transcript and protein sequence files with proper feature IDs
cat pdom.maker.output/pdom_datastore/PdomSCFr1.2-*/PdomSCFr1%2E2-*.maker.transcripts.fasta \
    | python seq-ids.py rnaids.txt > pdom-annot-r1.2-transcripts.fasta
cat pdom.maker.output/pdom_datastore/PdomSCFr1.2-*/PdomSCFr1%2E2-*.maker.proteins.fasta \
    | python seq-ids.py rnaids.txt > pdom-annot-r1.2-proteins.fasta
```

------

[![Creative Commons License](https://i.creativecommons.org/l/by/4.0/88x31.png)][ccby4]  
This work is licensed under a [Creative Commons Attribution 4.0 International License][ccby4].


[pdomproj]: https://github.com/PdomGenomeProject
[Maker annotation pipeline]: http://www.yandell-lab.org/software/maker.html
[ccby4]: http://creativecommons.org/licenses/by/4.0/
