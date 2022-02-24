import os
from tqdm import tqdm

names_extraction_file = '/projectnb/multilm/yusuf/racial_bias/LexisNexis/extracted_final.csv'
target_folder = '/projectnb/multilm/thdaryan/racial_bias/names_extraction_splitted'
chunk_size = 15000000
    
with open(names_extraction_file, encoding='utf8') as infile:
    i = 0
    split = 0
    list_line = []
    for line in tqdm(infile):
        if (i==0):
            print(line)
    
        list_line.append(line)
        if (i==chunk_size):
            with open(os.path.join(target_folder, f'names_extraction_{split}'), 'w+', encoding='utf8') as outfile:
                for item in list_line:
                    outfile.write(item)

            i = 0
            list_line = []
            split+=1
        
        i+=1
      
