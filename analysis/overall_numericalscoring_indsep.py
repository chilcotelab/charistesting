import pandas as pd

snr = pd.read_csv('numericalscoring/snr_scores.csv')
contrast = pd.read_csv('numericalscoring/contrast_scores.csv')
for col in contrast.columns:
    if col not in ['Annuli', 'Subsections', 'Movement', 'Numbasis', 'Corr_Smooth', 'Highpass'] and 'Score' not in col:
        del newdf[col]

overall = snr.merge(contrast, how='outer', on=['Annuli', 'Subsections', 'Movement', 'Numbasis',
                                               'Corr_Smooth', 'Highpass'], suffixes=['_snr', '_contrast'])

sorted_by_score = overall.sort_values(by='Overall Score', ascending=False, ignore_index=True)
sorted_by_score.to_csv('numericalscoring/overall_scores_indsep.csv', index=False)