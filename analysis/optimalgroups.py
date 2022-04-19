import numpy as np
import sys
import pandas as pd
import itertools

n = int(sys.argv[1])  # how big of parameter sets we're checking
csvfile = sys.argv[2]
numrows = int(sys.argv[3])  # how many parameter sets are we using for combinations
numcombos = int(np.prod([numrows - k for k in range(n)]) / np.prod(np.arange(n) + 1))
print(f'{numcombos} combinations will be checked.')  # so that if it's like a trillion then I just kill the script

columnnames = ['HD SNR', 'HD Contrast', 'HR SNR', 'HR Contrast', 'HIP SNR', 'HIP Contrast', 'Kappa SNR',
               'Kappa Contrast']
df = pd.read_csv(csvfile)[:numrows]
indexcombos = itertools.combinations(np.arange(numrows), n)
data_to_save = {'Params': list(), 'Threshold': list(), 'Average': list(), 'Overall': list()}
for ic in indexcombos:
    subdf = df.iloc[list(ic), :]
    fullmin = np.min([np.min(subdf[col]) for col in columnnames])
    average = np.mean(subdf['Average'])
    paramgroups = list()
    for idx in range(len(ic)):
        paramgroups.append(tuple([df.iloc[idx, k] for k in range(7)]))
    data_to_save['Params'].append(str(paramgroups))
    data_to_save['Threshold'].append(fullmin)
    data_to_save['Average'].append(average)
    data_to_save['Overall'].append(np.mean([fullmin, fullmin, average]))

broken_up_params = [list() for _ in range(n)]
for pset in data_to_save['Params']:
    parens = list()
    for i in range(len(pset)):
        if pset[i] in ['(', ')']:
            parens.append(i)
    pts = [f'({pset[parens[2*j]: parens[2*j + 1] + 1][4:]}' for j in range(int(len(parens) / 2))]
    assert len(pts) == len(broken_up_params)
    for k in range(n):
        broken_up_params[k].append(pts[k])
del data_to_save['Params']

combined = pd.DataFrame(data_to_save)
for m, psets in enumerate(broken_up_params):
    combined.insert(m, f'Params {m + 1}', psets)
to_csv = combined.sort_values('Overall', ascending=False, ignore_index=True)
to_csv.to_csv('groupscores.csv', index=False)
