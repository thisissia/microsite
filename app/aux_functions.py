import math
import numpy as np
from app.Classifier import BayesianUpdate
import pandas as pd


def worker(gap_g, gap_b, duration_g, duration_b, gaps, duration, prior, i, queue):
    classifier = BayesianUpdate(gap_g, gap_b, duration_g, duration_b)
    classifier.setPrior(prior)
    for ix, v in enumerate(gaps):
        classifier.predict(v, duration[ix])
    queue.put([i, classifier.evaluate()])


def xlsxparser(df):
    df_headers = df.columns.levels[0].values
    durations = []
    gaps = []
    ts = []
    te = []
    si = []
    for file_name in df_headers:
        gap, duration, tss, tes, sis = get_durations(df[file_name])
        durations.append(duration)
        gaps.append(gap)
        ts.append(tss)
        te.append(tes)
        si.append(sis)
    return gaps, durations, ts, te, si


def get_durations(file):
    gaps = []
    duration = []
    ts = []
    te = []
    si = []
    current_speaker = file['speaker_id'].head(n=1)[0]
    timeTo = file['time_start'].head(n=1)[0]
    for index, row in file.iterrows():
        if np.isnan(row['speaker_id']):
            break
        else:
            ts.append(row['time_start'])
            te.append(row['time_end'])
            si.append(row['speaker_id'])
            if row['speaker_id'] != current_speaker:
                gaps.append(math.log2(row['time_diff']))
                duration.append(math.log2(file.at[index-1, 'time_end']-timeTo))
                current_speaker = row['speaker_id']
                timeTo = file.at[index, 'time_start']
    if len(gaps) == 0:
        gaps.append(-5)
        duration.append(-5)
    return gaps, duration, ts, te, si


def xlsxpars(field):
    try:
        df = pd.read_excel(field.data, header=[0,1])
        df_headers = df.columns.levels[0].values
        for file_name in df_headers:
            if len(df[file_name].count()) != 4:
                return [False, "Conversation names not unique or the file is not correctly formatted."]
        if len(df.columns.levels[1].values) != 4:
            return [False, "Conversation names not unique or the file is not correctly formatted."]

        if not {'time_start', 'time_end', 'time_diff', 'speaker_id'}.issubset(df.columns.levels[1].values):
            return [False, "File must have the following sub-heading: time_start, time_end, time_diff and speaker_id."]
        return [True, df]
    except:
        return [False, "File is not in the correct format."]


def xlsxpars2(field):
    try:
        df = pd.read_excel(field.data, header=[0,1])
        if len(df.columns.levels[1].values) != 4:
            return [False, "Conversation names not unique or the file is not correctly formatted."]

        if not {'time_start', 'time_end', 'time_diff', 'speaker_id'}.issubset(df.columns.levels[1].values):
            return [False, "File must have the following sub-heading: time_start, time_end, time_diff and speaker_id."]
        return [True, df]
    except:
        return [False, "File is not in the correct format"]



if __name__ == '__main__':
    df = pd.read_excel('/Users/s150890/Documents/UCL/Msc/dissertation/UCL_IXN_NHS_INTERMEDIATE-master/good_dialogue_93_conv_wrd_from2_speaker_gap.xlsx',  header=[0,1])
    xlsxparser(df)