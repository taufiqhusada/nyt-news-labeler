#!/bin/bash -l

#$ -P multilm
#$ -l h_rt=99:00:00   # Specify the hard time limit for the job
#$ -pe omp 14
#$ -l mem_per_core=12G
#$ -N nyt_pararel_alligned
#$ -j y               # Merge the error and output streams into a single file
#$ -V
#$ -m e

python label_news_one_split.py 0 &
python label_news_one_split.py 1 &
python label_news_one_split.py 2 &
python label_news_one_split.py 3 &
python label_news_one_split.py 4 &
python label_news_one_split.py 5 &
python label_news_one_split.py 6 &
python label_news_one_split.py 7 &
python label_news_one_split.py 8 &
python label_news_one_split.py 9 &
python label_news_one_split.py 10 &
python label_news_one_split.py 11 &
wait
python label_news_one_split.py 12 &
python label_news_one_split.py 13 &
python label_news_one_split.py 14 &
python label_news_one_split.py 15 &
python label_news_one_split.py 16 &
python label_news_one_split.py 17 &
python label_news_one_split.py 18 &
python label_news_one_split.py 19 &
python label_news_one_split.py 20 &
python label_news_one_split.py 21 &
python label_news_one_split.py 22 &
python label_news_one_split.py 23 &
wait
