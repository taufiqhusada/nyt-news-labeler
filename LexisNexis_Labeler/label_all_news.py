import datetime as dt
from typing import Dict, List
from tqdm import tqdm

import sys
import os
import pandas as pd

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

data_path = '/projectnb/multilm/thdaryan/racial_bias/complete_raw_data_unique'
list_files = [f'LexisNexis_BostonMedia_NewsArticles_unique_{i}.csv' for i in range(20)]
    
for filename in list_files:
    try:
        outfile = open(f'result/labels_{filename[:-4]}.csv', 'w')
        outfile.write('doc_id,label_1,score_1,label_2,score_2,label_3,score_3,label_4,score_4,label_5,score_5\n')

        print(filename)
        csv_path = os.path.join(data_path, filename)
        try:
            df = pd.read_csv(csv_path, error_bad_lines=False,  encoding='utf8', engine='python')
            print(df.head(1))
            doc_ids = df['DOC-ID'].values
        except:
            df = pd.read_csv(csv_path, error_bad_lines=False,  encoding='utf8', engine='python', names=['hl1','author','lede','body','DOC-ID','pubDay','pubMonth','pubYear','pubName','filename','Unique_Id'])
            print(df.head(1))
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

            outfile.write(str(doc_ids[i]))
            outfile.write(',')
            outfile.write(','.join(outputs_this_id))
            outfile.write('\n')
            

        outfile.close()

    except Exception as e:
        with open('result/errors.txt', 'w') as f:
            print(filename, str(e))
            f.write(filename + " " + str(e))
