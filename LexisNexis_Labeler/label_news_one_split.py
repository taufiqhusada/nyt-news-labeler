import datetime as dt
from typing import Dict, List
from tqdm import tqdm

import sys
import os
import pandas as pd
import gc
import glob
import numpy as np

def read_file(filename):
    df = pd.read_csv(filename, error_bad_lines=False,  encoding='utf8', engine='python')
    df.fillna('nothing',inplace=True)
    return df

sys.path.append('..')
from models import (
    SELF_TEST_INPUT,
    Word2vecModel,
    Descriptors600Model,
    Scaler)

# Load the models into memory
word2vec_model = Word2vecModel()
scaler = Scaler()

MODEL_ALL = Descriptors600Model(word2vec_model=word2vec_model, scaler=scaler)

text = "Federal agents show stronger force at Portland protests despite order to withdraw"

result = MODEL_ALL.predict(text)
for x in result:
    print(x.label)
    print(x.score)

file_split = sys.argv[1] 
filename = f'/projectnb/multilm/thdaryan/racial_bias/names_extraction_splitted/names_extraction_{file_split}.csv'

with open(f'result_alligned/extracted_topic_{file_split}.tsv', 'w+') as outfile:
    outfile.write('id_from_name_extraction\tDOC-ID\tstart\tend\tsource_type\tlabel\tscore\n')

id_from_name_extraction = 0
for df_chunk in tqdm(pd.read_csv(filename, chunksize=10**4, header=None)):
    try:
        df_chunk.rename(columns={0: 'id_from_name_extraction', 1:'sent', 2:'names', 3:'start', 4:'end', 5:'source_type', 6:'DOC-ID'}, inplace=True)
        print(df_chunk.head())

        labels = []
        scores = []
        ids = []

        for sent in tqdm(df_chunk['sent'].values):
            result = MODEL_ALL.predict(str(sent))[0]
            
            labels.append(result.label)
            scores.append(result.score)

        df_to_save = pd.DataFrame({'id_from_name_extraction':df_chunk['id_from_name_extraction'].values, 'DOC-ID':df_chunk['DOC-ID'].values, 'start': df_chunk['start'].values, 
                                  'end': df_chunk['end'].values, 'label': labels, 'score': scores})
        print(df_to_save.head())
        df_to_save.to_csv(f'result_alligned/extracted_topic_{folder_name}.tsv', mode='a', header= False, sep='\t')
        
        del df_chunk, df_to_save
        gc.collect()
    except Exception as e:
        with open(f'result_alligned/errors_{file_split}.txt', 'a') as f:
            print(filename, str(e))
            f.write(filename + " " + str(e) + '\n')                  


