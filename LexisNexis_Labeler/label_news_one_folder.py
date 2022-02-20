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

folder_name =  sys.argv[1] 
list_files = glob.glob(f'/projectnb/multilm/yusuf/racial_bias/LexisNexis/output/data/{folder_name}/*.csv')
list_files = np.sort(list_files)

with open(f'result_pararel/extracted_topic_{folder_name}.csv', 'w') as outfile:
    outfile.write('doc_id,label_1,score_1,label_2,score_2,label_3,score_3,label_4,score_4,label_5,score_5\n')

for filename in tqdm(list_files):
    print(filename)
    try:
        df = read_file(filename)
        doc_ids = df['DOC-ID'].values
        docs = df['lede'].values

        tuple_id_and_outputs = []
        for i in range(len(doc_ids)):
            if (docs[i]==None):
                continue

            result = MODEL_ALL.predict(str(docs[i]))
            outputs_this_id = []
            for x in result:
                outputs_this_id.append(x.label)
                outputs_this_id.append(str(x.score))

            tuple_id_and_outputs.append((str(doc_ids[i]), outputs_this_id))
        
        with open(f'result_pararel/extracted_topic_{folder_name}.csv', 'a') as outfile:
            for (id, outputs_this_id) in tuple_id_and_outputs:
                outfile.write(id)
                outfile.write(',')
                outfile.write(','.join(outputs_this_id))
                outfile.write('\n')

        del df, doc_ids, docs
        gc.collect()

    except Exception as e:
        with open(f'result_pararel/errors_{folder_name}.txt', 'a') as f:
            print(filename, str(e))
            f.write(filename + " " + str(e) + '\n')
