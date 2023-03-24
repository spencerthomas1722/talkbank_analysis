from collections import defaultdict
import pandas
import re
import tbdb
import random


def echoed_utterances(transcript):
    lines = utterances(transcript)

    childs_last_line = ''
    mothers_last_line = ''
    results = {'c<m': 0,  # number of times child repeats part of mot's utterance
               'c=m': 0,  # number of times child repeats mother's whole utterance
               'm<c': 0,  # same, but mother repeating child
               'm=c': 0,
               '=last': 0,  # number of times a line is (at least partially) repeated
               'child_lines': 0, 'mother_lines': 0, 'total_lines': 0}
    last_line = ''
    for line in lines:
        if line[4] == 'Target_Child':  # child speaking
            results['child_lines'] += 1
            line = re.sub(r'[^\w\s\'\_\-]', '', line[7]).strip()  # remove punct + extra whitespace
            if line in mothers_last_line:
                results['c<m'] += 1
                if line == mothers_last_line:
                    results['c=m'] += 1
            childs_last_line = line
        else:  # other person speaking
            results['mother_lines'] += 1
            line = re.sub(r'[^\w\s\'\_\-]', '', line[7]).strip()  # remove punct + extra whitespace
            if line in childs_last_line:
                results['m<c'] += 1
                if line == childs_last_line:
                    results['m=c'] += 1
            mothers_last_line = line
        if line == last_line:
            results['=last'] += 1
        last_line = line
    return results


def analyze_repeated_vocab(transcript, split_morphemes=False):
    lines = utterances(transcript)
    childs_words = {'own': defaultdict(int), 'mothers': defaultdict(int)}
    childs_last_line = ''
    mothers_last_line = ''
    for line in lines:
        if split_morphemes:
            line = line.replace('~', ' ')  # replace morpheme boundary with whitespace so it gets split
        if line[4] == 'Target_Child':
            line = re.sub(r'[^\w\s\'\_\-]', '', line[7]).strip()  # remove punct + extra whitespace
            words = line.split()
            if line in mothers_last_line:
                for word in words:
                    childs_words['mothers'][word] += 1
            else:
                for word in words:
                    childs_words['own'][word] += 1
        else:
            line = re.sub(r'[^\w\s\'\_\-]', '', line[7]).strip()  # remove punct + extra whitespace
            mothers_last_line = line
    output_percentages = {}
    combined = set(childs_words['own']).union(set(childs_words['mothers']))
    for word in combined:
        if word in childs_words['own'].keys():
            if word in childs_words['mothers'].keys():
                output_percentages[word] = childs_words['own'][word] / (childs_words['own'][word] + childs_words['mothers'][word])
            else:
                output_percentages[word] = 1  # child only uses word on their own
        else:
            output_percentages[word] = 0  # word only appears when repeating interlocutor
    print(f'total vocab: {len(combined)}; independent vocab: {len(childs_words["own"])}')
    return sorted(output_percentages, key=lambda k: output_percentages[k], reverse=True)


"""given transcript metadata, including file name, get the utterances."""
def utterances(transcript, reformat=False):
    fpath = transcript[0].split('/')
    utters = tbdb.getUtterances({'corpusName': fpath[0], 'corpora': [fpath]})['data']
    # this gets us a bunch of repeated lines; we normalize them so that we can remove extras.
    for utter in utters:
        utter[7] = utter[7].replace('_', '')  # e.g. 'i want milk_ball' => 'i want milkball', for consistency
    try:
        out_utters = [utters[0]]
    except IndexError:
        return []
    for utter in utters[1:]:
        if out_utters[-1] != utter:
            out_utters.append(utter)  # sents are indexed, so genuine repetitions will be left in
    if reformat:
        out_utters = [f'*{utt[3]}:	{utt[7]}' for utt in out_utters]  # recreate lines
    return out_utters


"""get the types, tokens, and type:token ratio for the target child within a given transcript"""
def ttr(transcript):
    fpath = transcript[0].split('/')
    lines = tbdb.getTokenTypes({'corpusName': fpath[0], 'corpora': [fpath]})
    lines = lines['data']
    lines = [line for line in lines if line[0] == 'Target_Child']
    types_dct = defaultdict(lambda: 0)
    for line in lines:
        token = line[-1]
        types_dct[token] += 1
    types = len(types_dct.keys())
    tokens = sum([j for i, j in types_dct.items()])
    return {'types': types, 'tokens': tokens, 'ttr': types/tokens}


"""obtain the MLU and MLT (if desired) for the child and non-child speakers in a given transcript"""
def meanlength(transcript, mlt=True, morpheme=False):
    lines = utterances(transcript)
    dct = defaultdict(lambda: {'morphemes': 0, 'utterances': 0, 'turns': 0})
    lastspeaker = None
    for line in lines:
        speaker = line[3]
        utterance = line[7]
        if speaker != 'CHI':
            speaker = 'MOT'
        if lastspeaker != speaker:
            dct[speaker]['turns'] += 1
        dct[speaker]['utterances'] += 1
        if morpheme:
            utterance = line.replace('~', ' ')
        dct[speaker]['morphemes'] += len(utterance.split())
        lastspeaker = speaker
    meanlengths = {}
    for speaker in dct.keys():
        meanlengths[speaker + '_mlu'] = dct[speaker]['morphemes'] / dct[speaker]['utterances']
        if mlt:
            meanlengths[speaker + '_mlt'] = dct[speaker]['morphemes'] / dct[speaker]['turns']
    return meanlengths


"""perform longitudinal data analysis on the .cha files in a directory"""
def longitudinal(analysis_func, search_options):
    transcripts = tbdb.getTranscripts(search_options)['data']
    all_results = {}
    total_result = defaultdict(lambda: 0) # result is a dict
    counts = defaultdict(lambda: 0)
    for transcript in transcripts:
        result = analysis_func(transcript)
        all_results[transcript[1]] = result
        for k in result.keys():
            total_result[k] += result[k]
            counts[k] += 1
    all_results['average'] = {k: (total_result[k]/counts[k]) for k in total_result.keys()}
    return all_results


"""given a set of sub-directories (names) within a corpus and a list of analysis functions,
perform data analysis of those functions on the files in each of those sub-directories"""
def multi_longitudinal(names, analysis_funcs):
    search_options = {'corpusName': 'asd', 'corpora': [['asd', 'English', 'Flusberg']], 'lang': ['eng'], 'activityType': ['toyplay'], 'groupType': 'TD'}
    all_results = {}
    for name in names:
        corpus = ['asd', 'English', 'Flusberg'] + [name]
        search_options['corpora'] = [corpus]
        for func in analysis_funcs:
            all_results[name][func.__name__] = longitudinal(func, search_options)
    with pandas.ExcelWriter('autism.xlsx', engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
        for name in names:
            for func in analysis_funcs:
                df = pandas.DataFrame.from_dict(all_results[name][func.__name__])
                df.to_excel(writer, sheet_name=name + '_' + func.__name__, index=True)


"""get results for one group of transcripts (the results of one transcript query)"""
def cross_section(transcripts, analysis_func, avg=True):
    counts = defaultdict(lambda: 0)
    cross_section_result = analysis_func(transcripts[0])
    for transcript in transcripts[1:]:
        result = analysis_func(transcript)
        for k in result.keys():
            counts[k] += 1
            try:
                cross_section_result[k] += result[k]
            except KeyError:
                cross_section_result[k] = result[k]
    if avg:
        for k in cross_section_result.keys():
            cross_section_result[k] /= counts[k]
    cross_section_result['n'] = len(transcripts)
    return cross_section_result


"""given search parameters for the TalkBank databases, 
(**kwargs, e.g. {'age': [40, 48, 60, 72, 84, 96, 108, 120]})
run a cross-sectional data analysis on each combination of parameters.
this is then saved to an excel file.
note: must create the correct file BEFOREHAND.
if we try to catch a FileNotFoundError and create the file on-the-fly, the new file will be ill-formed."""
def multi_cross_section(analysis_funcs, max_num_transcripts=100, **kwargs):
    multi_cross_section_results = {func.__name__: {} for func in analysis_funcs}
    search_options = {'corpusName': 'childes', 'corpora': [['childes', 'Eng-NA']], 'lang': ['eng'],
                      'age': [40], 'activityType': ['toyplay'], 'groupType': ['TD']}
    for kw in kwargs.keys():
        for argi in range(len(kwargs[kw])):
            search_options[kw] = kwargs[kw][argi]
            # get one set of transcripts for all functions
            all_transcripts = tbdb.getTranscripts(search_options)['data']
            counts = defaultdict(lambda: 0)
            if len(all_transcripts) > max_num_transcripts:
                transcripts = random.sample(all_transcripts, max_num_transcripts)
                all_transcripts = [t for t in all_transcripts if
                                   t not in transcripts]  # prevents double-sampling further on
                for transcript in transcripts:
                    # remove transcript without text
                    if transcript[3] is not None and ('notrans' in transcript[3] or 'unlinked' in transcript[3]):
                        new_transcript = random.choice(all_transcripts)
                        all_transcripts.remove(new_transcript)
                        transcripts.append(new_transcript)
                        transcripts.remove(transcript)
            else:
                transcripts = all_transcripts
                for transcript in transcripts:
                    if transcript[3] is not None and ('notrans' in transcript[3] or 'unlinked' in transcript[3]):
                        transcripts.remove(transcript)  # remove transcript without text
            for analysis_func in analysis_funcs:
                result = cross_section(transcripts, analysis_func)
                for k in result.keys():
                    counts[k] += 1
                print(f'{analysis_func.__name__}: {search_options["groupType"]} children with {kw}={kwargs[kw][argi]} (n={result["n"]}): {result}')
                multi_cross_section_results[analysis_func.__name__][str(kwargs[kw][argi])] = result
    for group in search_options['groupType']:
        out_fname = group.lower() + '.xlsx'
        # note: must create the correct file BEFOREHAND.
        # if we try to catch a FileNotFoundError and create the file on-the-fly, the new file will be ill-formed.
        with pandas.ExcelWriter(out_fname, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
            for analysis_func in analysis_funcs:
                sheetname = f'{analysis_func.__name__}'
                df = pandas.DataFrame(multi_cross_section_results[analysis_func.__name__], index=multi_cross_section_results.keys())
                df.to_excel(writer, sheet_name=sheetname, index=True)


if __name__ == "__main__":
    names = ['Brett', 'Jack', 'Mark', 'Rick', 'Roger', 'Stuart']
    # ages (in months) of the transcripts we want to look at
    ages = [40, 45, 48, 55, 60, 66, 68, 72, 81, 84, 89, 91, 96, 104, 108, 116]
    multi_longitudinal(names, analysis_funcs=[meanlength, ttr, echoed_utterances])
    multi_cross_section(analysis_funcs=[meanlength, ttr, echoed_utterances], age=ages)
