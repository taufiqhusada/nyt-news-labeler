#!/bin/bash -l

#$ -P multilm
#$ -l h_rt=200:00:00   # Specify the hard time limit for the job
#$ -pe omp 12
#$ -l mem_per_core=8G
#$ -N nyt_labeler_pararel
#$ -j y               # Merge the error and output streams into a single file
#$ -V
#$ -m e

python label_news_one_folder.py 352488 &
python label_news_one_folder.py 315415 &
python label_news_one_folder.py 316091 &
python label_news_one_folder.py 387410 &
python label_news_one_folder.py 152974 &
python label_news_one_folder.py 302177 &
python label_news_one_folder.py 155406 &
python label_news_one_folder.py 315851 &
python label_news_one_folder.py 270099 &
python label_news_one_folder.py 279925 &
python label_news_one_folder.py 145223 &
python label_news_one_folder.py 8110 &
python label_news_one_folder.py 388135 &
python label_news_one_folder.py 469785 &
python label_news_one_folder.py 262350 &
python label_news_one_folder.py 364990 &
python label_news_one_folder.py 279929 &
python label_news_one_folder.py 313487 &
python label_news_one_folder.py 152787 &
python label_news_one_folder.py 308103 &
wait
