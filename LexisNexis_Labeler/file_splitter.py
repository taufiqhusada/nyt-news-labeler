names_extraction_file = /projectnb/multilm/yusuf/racial_bias/LexisNexis/extracted_final.csv
chunk_size = 500000
    
with open(names_extraction_file, 'w') as infile:
    i = 0
    split = 0
    list_line = []
    for line in infile:
        if (i==0):
            print(line)
    
        list_line.append(line)
        if (i==chunk_size):
            with open(f'names_extraction_{split}', 'w') as outfile:
                for item in list_line:
                    outfile.write(item)

            i = 0
            list_line = []
            split+=1
        
        i+=1
      
