import numpy as np
import pandas as pd

from etl import load_smac_data, clean_smac_data


def main():
    raw_data = load_smac_data('raw')
    clean_data_1 = load_smac_data('clean')
    clean_data_2 = clean_smac_data(load_smac_data('clean'))

    print('Meta-Analysis of Data Cleaning Efforts:')
    for key in raw_data.keys():
        if key in {'Codebook', 'digital'}:
            continue

        raw_sheet = raw_data[key]
        clean_1_sheet = clean_data_1[key]
        clean_2_sheet = clean_data_2[key]

        column_labels = list(raw_sheet.columns)

        diff_1 = raw_sheet.values != clean_1_sheet.values
        diff_2 = clean_1_sheet.values != clean_2_sheet.values
        diff_3 = raw_sheet.values != clean_2_sheet.values

        print(f'Sheet: {key}')

        print('\tSheet Level Statistics:')
        print(f'\t\tRows:            {diff_1.shape[0]}')
        print(f'\t\tColumns:         {diff_1.shape[1]}')
        print(f'\t\tValues:          {np.prod(diff_1.shape)}')
        print(f'\t\tManual Edits:    {diff_1.sum()} ({100 * diff_1.sum() / np.prod(diff_1.shape):0.4f}%)')
        print(f'\t\tAutomated Edits: {diff_2.sum()} ({100 * diff_2.sum() / np.prod(diff_2.shape):0.4f}%)')
        print(f'\t\tTotal Edits:     {diff_3.sum()} ({100 * diff_3.sum() / np.prod(diff_3.shape):0.4f}%)')

        print('\n\tRow Level Statistics:')
        row_diff_1 = diff_1.sum(axis=1)
        print(f'\t\tSummary of Manual Edits:')
        display_describe(pd.Series(row_diff_1).describe(), tab_level=3)

        row_diff_2 = diff_2.sum(axis=1)
        print(f'\t\tSummary of Automated Edits:')
        display_describe(pd.Series(row_diff_2).describe(), tab_level=3)

        row_diff_3 = diff_3.sum(axis=1)
        print(f'\t\tSummary of Total Edits:')
        display_describe(pd.Series(row_diff_3).describe(), tab_level=3)

        print('\n\tColumn Level Statistics:')
        col_diff_1 = diff_1.sum(axis=0)
        print(f'\t\tSummary of Manual Edits:')
        display_describe(pd.Series(col_diff_1).describe(), tab_level=3)

        col_diff_2 = diff_2.sum(axis=0)
        print(f'\t\tSummary of Automated Edits:')
        display_describe(pd.Series(col_diff_2).describe(), tab_level=3)

        col_diff_3 = diff_3.sum(axis=0)
        print(f'\t\tSummary of Total Edits:')
        display_describe(pd.Series(col_diff_3).describe(), tab_level=3)
        print()


def display_describe(df, columns=None, tab_level=0):
    if columns is None:
        columns = ['mean', 'std', 'min', '25%', '50%', '75%', 'max']

    tab_str = '\t' * tab_level
    print(
        tab_str +
        df[columns].reset_index().to_string(header=None, index=None).replace('\n', f'\n{tab_str}')
    )


if __name__ == '__main__':
    main()
