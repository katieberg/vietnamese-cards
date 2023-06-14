import uuid
import os
import os.path

def add_id():
    file_name = 'notes/anki_sample_word_upfront.txt'
    temp_file_name = 'notes/anki_sample_word_upfront_temp.txt'
    with open(file_name, 'r') as f:
        lines = f.readlines()
    with open(temp_file_name, 'w') as temp:
        for line in lines:
            line = line.strip()
            segments = line.split(';')
            if len(segments) == 5:
                segments = [*segments, str(uuid.uuid4())]
            new_line = ';'.join(segments)
            temp.write(f'{new_line}\n')
        
    ## do mv magic
    os.system(f'mv {file_name} {file_name}_old')
    os.system(f'mv {temp_file_name} {file_name}')
    os.system(f'rm {file_name}_old')


def main():
    add_id()

if __name__ == '__main__':
    main()
    