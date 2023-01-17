import os
f = open('notes/temp.text', 'r')
for l in f.readlines():
    segments = l.split(';')
    second_segment = ''
    for c in segments[1]:
        if c == ' ':
            second_segment = second_segment + ' '
        else:
            second_segment = second_segment + '_'
    
    new_line = ';'.join([segments[0], second_segment, segments[2], segments[3], segments[4].strip()])
    print(new_line)