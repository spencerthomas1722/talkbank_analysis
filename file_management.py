"""note: this code was used when manipulating files that i had downloaded onto my own file system.
it is not meant to be used with transcripts obtained with TBDBpy."""


"""some dialogue lines in the .cha files are split into 2+ lines due to length.
this interferes with parsing them, so we'll just consolidate each line of dialogue into one line."""
def fixcha(fname):
    with open(fname, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    out_lines = []
    last_line = lines[0]
    for line in lines[1:]:
        if line.startswith('\t'):
            last_line += ' ' + line
        else:
            last_line = line
            out_lines.append(line)
    with open(fname, 'w', encoding='utf-8') as f:
        f.writelines(out_lines)


"""get just the morpheme level for a given transcript"""
def process_mor(fname):
    with open(fname, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # get just morphemes
    out_lines = []
    for line in lines:
        if line.startswith('*'):
            new_line = line[:5]  # will get just e.g. '*CHI:'
        elif line.startswith('%mor'):
            new_line += line[5:]  # will get everything after '%mor:'
            out_lines.append(new_line)
    # save as separate file
    fname = fname.replace('.cha', '.mor')
    with open(fname, 'w', encoding='utf-8') as f:
        f.writelines(out_lines)
