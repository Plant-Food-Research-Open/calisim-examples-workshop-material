#!/bin/bash
#####################################################
## Visulisation of TEgenomeSimulator mode 0 output ##
#####################################################

# Prerequisite: 
# samtools
# R (4.3.3)

# first: neviagate to the output folder: demo_m0 
cd demo_m0

# need to use full path of input files and directory to create the report
demo_dir=$(pwd)
genome_fa=$demo_dir/TEgenomeSimulator_demo_m0_1_5_result/demo_m0_1_5_genome_sequence_out_final.fasta
repeat_fa=$demo_dir/TEgenomeSimulator_demo_m0_1_5_result/demo_m0_1_5_repeat_sequence_out_final.fasta
repeat_gff=$demo_dir/TEgenomeSimulator_demo_m0_1_5_result/demo_m0_1_5_repeat_annotation_out_final.gff
prefix="demo_m0"
outdir=$demo_dir/report
mkdir -p $outdir

Rscript ../run_tegs_report.R ${genome_fa} ${repeat_fa} ${repeat_gff} ${prefix} ${outdir}