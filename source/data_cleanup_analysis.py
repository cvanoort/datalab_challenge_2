from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from etl import load_smac_data, clean_smac_data


def main():
    raw_data = load_smac_data('raw')
    clean_data_1 = load_smac_data('clean')
    clean_data_2 = clean_smac_data(load_smac_data('clean'))

    sheet_stats = dict()
    for key in raw_data.keys():
        if key in {'Codebook', 'digital'}:
            continue

        raw_sheet = raw_data[key]
        clean_1_sheet = clean_data_1[key]
        clean_2_sheet = clean_data_2[key]

        sheet_stats[key] = get_sheet_stats(raw_sheet, clean_1_sheet, clean_2_sheet)
    global_stats = calculate_global_stats(sheet_stats)

    with pd.option_context('display.precision', 2):
        report(global_stats, sheet_stats)

    make_column_bar_figure(
        sheet_stats,
        filter_upper=100.,
        filter_lower=1.,
    )


def calculate_global_stats(name2sheet_stats):
    global_stats = Counter()

    for name, sheet_stats in name2sheet_stats.items():
        sheet_stats = Counter(sheet_stats)
        for key in ['row_stats', 'col_stats', 'col_labels', 'col_total_rel_vals']:
            sheet_stats.pop(key)

        global_stats += sheet_stats

    global_stats['n_manual_edits_rel'] = 100. * global_stats['n_manual_edits'] / global_stats['n_values']
    global_stats['n_auto_edits_rel'] = 100. * global_stats['n_auto_edits'] / global_stats['n_values']
    global_stats['n_total_edits_rel'] = 100. * global_stats['n_total_edits'] / global_stats['n_values']

    return dict(global_stats)


def get_sheet_stats(raw_sheet, clean_1_sheet, clean_2_sheet):
    diff_1 = raw_sheet.values != clean_1_sheet.values
    diff_2 = clean_1_sheet.values != clean_2_sheet.values
    diff_3 = raw_sheet.values != clean_2_sheet.values

    n_rows = diff_1.shape[0]
    n_cols = diff_1.shape[1]
    n_values = np.prod(diff_1.shape)

    n_manual_edits = diff_1.sum()
    n_manual_edits_rel = 100. * n_manual_edits / n_values
    n_auto_edits = diff_2.sum()
    n_auto_edits_rel = 100. * n_auto_edits / n_values
    n_total_edits = diff_3.sum()
    n_total_edits_rel = 100. * n_total_edits / n_values

    row_diff_1 = diff_1.sum(axis=1)
    row_diff_2 = diff_2.sum(axis=1)
    row_diff_3 = diff_3.sum(axis=1)
    row_manual = pd.Series(row_diff_1).describe()
    row_manual_rel = 100. * row_manual / n_cols
    row_auto = pd.Series(row_diff_2).describe()
    row_auto_rel = 100. * row_auto / n_cols
    row_total = pd.Series(row_diff_3).describe()
    row_total_rel = 100. * row_total / n_cols
    row_stats = pd.concat(
        [row_manual, row_manual_rel, row_auto, row_auto_rel, row_total, row_total_rel],
        axis=1,
    )
    row_stats.columns = [
        'Row Manual',
        'Row Manual Rel.',
        'Row Auto',
        'Row Auto Rel.',
        'Row Total',
        'Row Total Rel.',
    ]

    col_diff_1 = diff_1.sum(axis=0)
    col_diff_2 = diff_2.sum(axis=0)
    col_diff_3 = diff_3.sum(axis=0)
    col_manual = pd.Series(col_diff_1).describe()
    col_manual_rel = 100. * col_manual / n_rows
    col_auto = pd.Series(col_diff_2).describe()
    col_auto_rel = 100. * col_auto / n_rows
    col_total = pd.Series(col_diff_3).describe()
    col_total_rel = 100. * col_total / n_rows
    col_stats = pd.concat(
        [col_manual, col_manual_rel, col_auto, col_auto_rel, col_total, col_total_rel],
        axis=1,
    )
    col_stats.columns = [
        'Col Manual',
        'Col Manual Rel.',
        'Col Auto',
        'Col Auto Rel.',
        'Col Total',
        'Col Total Rel.',
    ]

    return {
        'n_rows': n_rows,
        'n_cols': n_cols,
        'n_values': n_values,
        'n_manual_edits': n_manual_edits,
        'n_manual_edits_rel': n_manual_edits_rel,
        'n_auto_edits': n_auto_edits,
        'n_auto_edits_rel': n_auto_edits_rel,
        'n_total_edits': n_total_edits,
        'n_total_edits_rel': n_total_edits_rel,
        'row_stats': row_stats,
        'col_stats': col_stats,
        'col_total_rel_vals': 100. * col_diff_3 / n_rows,
        'col_labels': list(raw_sheet.columns),
    }


def report(global_stats, name2sheet_stats):
    print('Meta-Analysis of Data Cleaning Efforts:')
    display_global_stats(global_stats)

    print('Sheet Level Statistics:')
    for name, sheet_stats in name2sheet_stats.items():
        display_sheet_stats(name, sheet_stats)


def display_global_stats(global_stats):
    print('Global Statistics:')
    print(f'\tRows:            {global_stats["n_rows"]:7d}')
    print(f'\tColumns:         {global_stats["n_cols"]:7d}')
    print(f'\tValues:          {global_stats["n_values"]:7d}')
    print(f'\tManual Edits:    {global_stats["n_manual_edits"]:7d} ({global_stats["n_manual_edits_rel"]:2.2f}%)')
    print(f'\tAutomated Edits: {global_stats["n_auto_edits"]:7d} ({global_stats["n_auto_edits_rel"]:2.2f}%)')
    print(f'\tTotal Edits:     {global_stats["n_total_edits"]:7d} ({global_stats["n_total_edits_rel"]:2.2f}%)')
    print()


def display_sheet_stats(sheet_name, sheet_stats):
    print('-' * 65)
    print(f'\tSheet Name: {sheet_name}')
    print(f'\tRows:            {sheet_stats["n_rows"]:7d}')
    print(f'\tColumns:         {sheet_stats["n_cols"]:7d}')
    print(f'\tValues:          {sheet_stats["n_values"]:7d}')
    print(f'\tManual Edits:    {sheet_stats["n_manual_edits"]:7d} ({sheet_stats["n_manual_edits_rel"]:2.2f}%)')
    print(f'\tAutomated Edits: {sheet_stats["n_auto_edits"]:7d} ({sheet_stats["n_auto_edits_rel"]:2.2f}%)')
    print(f'\tTotal Edits:     {sheet_stats["n_total_edits"]:7d} ({sheet_stats["n_total_edits_rel"]:2.2f}%)')
    print('\n\tRow Level Statistics:')
    display_describe(sheet_stats["row_stats"], tab_level=2, header=True, index=True)
    print('\n\tColumn Level Statistics:')
    display_describe(sheet_stats["col_stats"], tab_level=2, header=True, index=True)
    print()


def display_describe(df, columns=None, tab_level=0, header=False, index=False):
    if columns is None:
        columns = ['mean', 'std', 'min', '25%', '50%', '75%', 'max']

    if isinstance(df, pd.Series):
        df = df[columns]
    elif isinstance(df, pd.DataFrame):
        df = df.loc[columns]
    else:
        raise TypeError(
            f'display_describe is only intended to operate on pandas Dataframe'
            f' and Series objects, but was given a {type(df)}!'
        )

    tab_str = '\t' * tab_level
    print(
        tab_str +
        df.to_string(header=header, index=index).replace('\n', f'\n{tab_str}')
    )


def make_column_bar_figure(
        sheet_stats,
        ignore_cols=None,
        save_path='../figures',
        save_name='impacted_columns.png',
        bar_width=1000,
        bar_spacing=200,
        filter_upper=None,
        filter_lower=None,
):
    labels = None
    values = None
    for sheet, stats in sheet_stats.items():
        labels_ = [f'{sheet} - {col_label}' for col_label in stats['col_labels']]
        values_ = stats['col_total_rel_vals']

        if labels and values:
            labels.extend(labels_)
            values.extend(values_)
        else:
            labels = labels_
            values = list(values_)

    zipped = list(zip(labels, values))

    # Sort alphabetically, then by values
    zipped.sort(key=lambda x: x[0])
    zipped.sort(key=lambda x: x[1])

    if ignore_cols:
        zipped = list(filter(lambda x: x[0] not in ignore_cols, zipped))

    print('Column Impact: Outliers')
    for label, value in reversed(zipped):
        if (value <= filter_lower) or (value >= filter_upper):
            print(f'\t{label}: {value}')

    filter_upper = filter_upper or (max(values) + 1)
    filter_lower = filter_lower or (min(values) - 1)
    zipped = list(filter(lambda x: filter_lower < x[1] < filter_upper, zipped))

    labels, values = zip(*zipped)

    bar_locs = np.arange(len(labels)) * bar_width

    plt.subplots()
    plt.barh(bar_locs, values, height=bar_width - bar_spacing)
    plt.yticks(bar_locs[::3], labels[::3])
    plt.title('Data Cleaning Impact By Column')
    plt.ylabel('Sheet: Column')
    plt.xlabel('Relative Change')
    plt.xlim(-5, 105)
    plt.tight_layout()

    path = Path(save_path) / save_name
    path.parent.mkdir(exist_ok=True, parents=True)

    plt.savefig(path, dpi=400, transparent=True)
    plt.close('all')


if __name__ == '__main__':
    main()
