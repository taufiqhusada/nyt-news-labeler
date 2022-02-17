import datetime as dt
from typing import Dict, List
from tqdm import tqdm

import sys
import os
import pandas as pd
import gc
import glob

def read_file(filename):
    df = pd.read_csv(filename, engine='python')
    df.fillna('nothing',inplace=True)
    return df

sys.path.append('..')
from models import (
    SELF_TEST_INPUT,
    Word2vecModel,
    DescriptorsAllModel,
    Scaler)

# Load the models into memory
word2vec_model = Word2vecModel()
scaler = Scaler()

MODEL_ALL = DescriptorsAllModel(word2vec_model=word2vec_model, scaler=scaler)

text = "Federal agents show stronger force at Portland protests despite order to withdraw"

result = MODEL_ALL.predict(text)
for x in result:
    print(x.label)
    print(x.score)

list_files = glob.glob('/projectnb/multilm/yusuf/racial_bias/LexisNexis/output/data/*/*.csv')
list_files = np.sort(list_files)

with open('result_full/extracted_topic_final.csv', 'w') as outfile:
    outfile.write('doc_id,label_1,score_1,label_2,score_2,label_3,score_3,label_4,score_4,label_5,score_5\n')

for filename in tqdm(list_files):
    print(filename)
    try:
        df = read_file(filename)
        doc_ids = df['DOC-ID'].values
        docs = df['lede'].values

        tuple_id_and_outputs = []
        for i in tqdm(range(len(doc_ids))):
            if (docs[i]==None):
                continue

            result = MODEL_ALL.predict(str(docs[i]))
            outputs_this_id = []
            for x in result:
                outputs_this_id.append(x.label)
                outputs_this_id.append(str(x.score))

            tuple_id_and_outputs.append((str(doc_ids[i]), outputs_this_id))
        
        with open('result_full/extracted_topic_final.csv', 'a') as outfile:
            for (id, outputs_this_id) in tuple_id_and_outputs:
                outfile.write(id)
                outfile.write(',')
                outfile.write(','.join(outputs_this_id))
                outfile.write('\n')

        del df, doc_ids, docs
        gc.collect()

    except Exception as e:
        with open('result_full/errors.txt', 'a') as f:
            print(filename, str(e))
            f.write(filename + " " + str(e) + '\n')
