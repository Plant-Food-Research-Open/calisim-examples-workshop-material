# Test TEGenomeSimulator reproducibility
# # Created "fake_repeat.fa" and "random_genome_chr_index_small.csv" in the test/input dir
```bash
ml conda 
conda activate TEgenomeSimulator
cd /workspace/cflthc/script/TEgenomeSimulator/TEgenomeSimulator
repeat="../test/input/fake_repeat.fa"
genomeindex="../test/input/random_genome_chr_index_small.csv"
outdir="/workspace/cflthc/script/TEgenomeSimulator/test/output"
```

## rpdctest01
```bash
prefix="rpdctest01"
python ./TEgenomeSimulator.py -M 0 -p $prefix -r $repeat -c $genomeindex -o $outdir > $prefix.log 2>&1
```
## rpdctest02
```bash
prefix="rpdctest02"
python ./TEgenomeSimulator.py -M 0 -p $prefix -r $repeat -c $genomeindex -o $outdir > $prefix.log 2>&1
```
## test reproducibility
```bash
test1=$outdir/TEgenomeSimulator_rpdctest01_result/rpdctest01_repeat_sequence_out_final.fasta
test2=$outdir/TEgenomeSimulator_rpdctest02_result/rpdctest02_repeat_sequence_out_final.fasta
cmp --silent $test1 $test2 || echo "files are different"
# two files are different
```
## manually checked $test1 and $test2. 
```bash
cat $test1
cat $test2
```
**It seems that the inconsistency occurred at choosing nucleotides for substitution.**

Inconsistency example in $test1:
> >Fake_repeat3#Fake/T15mer_TE0000004#Fake/T15mer [Location=chr1:73-87;Identity=0.89;Integrity=1.0]
> TTTTTTTATTTTTTT
The corresponding match in $test2:
> >Fake_repeat3#Fake/T15mer_TE0000004#Fake/T15mer [Location=chr1:73-87;Identity=0.89;Integrity=1.0]
> TTTTTTTCTTTTTTT

Another example in $test1:
> >Fake_repeat1#Fake/A20mer_TE0000007#Fake/A20mer [Location=chr2:16-21;Identity=0.84;Integrity=0.3]
> TTTTTA
The corresponding match in $test2:
> >Fake_repeat1#Fake/A20mer_TE0000007#Fake/A20mer [Location=chr2:16-21;Identity=0.84;Integrity=0.3]
> TTTTTC

Third example in $test1
> >Fake_repeat1#Fake/A20mer_TE0000009#Fake/A20mer [Location=chr2:37-56;Identity=0.81;Integrity=1.0]
> TTTTTTTTTTCTTTATTTTT
The corresponding match in $test2:
> >Fake_repeat1#Fake/A20mer_TE0000009#Fake/A20mer [Location=chr2:37-56;Identity=0.81;Integrity=1.0]
> TTTTTTTTTTGTTTCTTTTT

Try more times.
```bash
prefix="rpdctest03"
python ./TEgenomeSimulator.py -M 0 -p $prefix -r $repeat -c $genomeindex -o $outdir > $prefix.log 2>&1
prefix="rpdctest04"
python ./TEgenomeSimulator.py -M 0 -p $prefix -r $repeat -c $genomeindex -o $outdir > $prefix.log 2>&1

test3=$outdir/TEgenomeSimulator_rpdctest03_result/rpdctest03_repeat_sequence_out_final.fasta
test4=$outdir/TEgenomeSimulator_rpdctest04_result/rpdctest04_repeat_sequence_out_final.fasta
cmp --silent $test3 $test4 || echo "files are different"
# two files are different
```

The small inconsistency might be caused by this line `new_base = random.choice(list(set(alphabet) - set(repeat_seq_list[pos])))` in the function of `add_base_changes()` in `TE_sim_random_insertion.py`. In this line `random` and `set()` are both used. But if the order of `set()` is not deterministic, the order could be different between each run, causing `random.choice()` to behave inconsistently, since it's choosing from a list in a different order each time.

Try the following solution:

Replacing the line `new_base = random.choice(list(set(alphabet) - set(repeat_seq_list[pos])))` to
```python
# Ensure deterministic order by sorting the list
choices = sorted(set(alphabet) - set(repeat_seq_list[pos]))
new_base = random.choice(choices)
```

Rerun the test.
```bash
prefix="rpdctest05"
python ./TEgenomeSimulator.py -M 0 -p $prefix -r $repeat -c $genomeindex -o $outdir > $prefix.log 2>&1
prefix="rpdctest06"
python ./TEgenomeSimulator.py -M 0 -p $prefix -r $repeat -c $genomeindex -o $outdir > $prefix.log 2>&1

test5=$outdir/TEgenomeSimulator_rpdctest05_result/rpdctest05_repeat_sequence_out_final.fasta
test6=$outdir/TEgenomeSimulator_rpdctest06_result/rpdctest06_repeat_sequence_out_final.fasta
cmp --silent $test5 $test6 || echo "files are different"
# two files are identical

test5=$outdir/TEgenomeSimulator_rpdctest05_result/rpdctest05_genome_sequence_out_final.fasta
test6=$outdir/TEgenomeSimulator_rpdctest06_result/rpdctest06_genome_sequence_out_final.fasta
cmp --silent $test5 $test6 || echo "files are different"
# two files are identical

```

