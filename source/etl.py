"""
"""

import argparse
import json
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
import pkg_resources
from symspellpy import SymSpell

import sierra_leone

# Global spell checker configuration
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = pkg_resources.resource_filename(
    "symspellpy",
    "frequency_dictionary_en_82_765.txt",
)
bigram_path = pkg_resources.resource_filename(
    "symspellpy",
    "frequency_bigramdictionary_en_243_342.txt",
)
# term_index is the column of the term and count_index is the column of the term frequency
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
sym_spell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)


def get_parser():
    def parse_bool(x):
        return x.lower() in {'true', 't', '1'}

    parser = argparse.ArgumentParser(
        description="Functions and tools to clean and load the SMAC data for Data Lab challenge 2.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        '--clean_data',
        type=parse_bool,
        default=True,
        help='Applies automated cleaning procedures to the SMAC data.',
    )
    parser.add_argument(
        '--data_kind',
        type=lambda x: x.lower(),
        default='clean',
        choices=['clean', 'raw'],
        help='Determines the data flavor that is loaded. '
             'clean has been manually curated and raw is unchanged.',
    )
    parser.add_argument(
        '--save_csvs',
        type=parse_bool,
        default=False,
        help='Saves data CSVs before automated cleaning has been applied.',
    )
    parser.add_argument(
        '--save_clean_csvs',
        type=parse_bool,
        default=False,
        help='Saves data CSVs after automated cleaning has been applied.',
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help='Determines the level of terminal output.'
    )

    return parser


def main(
        clean_data=True,
        data_kind='clean',
        save_clean_csvs=False,
        save_csvs=False,
        verbose=False,
):
    dfs = load_smac_data(data_kind=data_kind)

    if save_csvs:
        for sheet, df in sorted(dfs.items()):
            df.to_csv(f'../data/{data_kind}/all_paper_data_{sheet.strip().replace(" ", "_")}.csv', index=False)

    if clean_data:
        dfs = clean_smac_data(dfs, verbose=verbose)

    for sheet_name in dfs.keys():
        if sheet_name in {'Codebook', 'digital'}:
            continue
        validate_sheet_locations(dfs, sheet_name=sheet_name, data_kind=data_kind, verbose=verbose)

    if verbose:
        print('Summary of cleaned sheets:')
        for label, df in sorted(dfs.items()):
            print(f'{label}:\n{df.dtypes}\n\n')

    if save_clean_csvs:
        for sheet, df in sorted(dfs.items()):
            df.to_csv(f'../data/{data_kind}/all_paper_data_{sheet.strip().replace(" ", "_")}_clean.csv', index=False)


def load_smac_data(data_kind='clean'):
    return {
        path.stem.replace('all_paper_data_', ''): pd.read_csv(path, parse_dates=[0])
        for path in sorted(Path(f'../data/{data_kind}').glob('*.csv'))
    }


def load_smac_data_old(path='../data/clean/all_paper_data.xlsx'):
    dfs = pd.read_excel(
        path,
        sheet_name=[
            'Trigger_NA',
            'Trigger_Ave',
            'Trigger Other',
            'Follow Up',
            'Follow Up Other',
        ],
    )

    dfs['Codebook'] = pd.read_excel(
        path,
        sheet_name='Codebook',
        skiprows=[0],
    )
    return dfs


def clean_smac_data(dfs, verbose=False):
    # Parse an additional date column
    dfs['Follow_Up'].Date_of_dep = pd.to_datetime(dfs['Follow_Up'].Date_of_dep)

    clean_int_col_map = IDDict({'o': 0, 'O': 0, 'nan': 0})
    for i in range(100):
        clean_int_col_map[i] = i

    dfs['Follow_Up'].Children = dfs['Follow_Up'].Children.map(clean_int_col_map)
    dfs['Follow_Up'].r_mc = dfs['Follow_Up'].r_mc.map(clean_int_col_map)
    dfs['Follow_Up'].r_fa = dfs['Follow_Up'].r_fa.map(clean_int_col_map)

    # Fill in the Children column when it is NA and Male_child + Female_child are not NA
    index = (
            dfs['Trigger_Ave'].Children.isna() &
            ~dfs['Trigger_Ave'].Male_child.isna() &
            ~dfs['Trigger_Ave'].Female_child.isna()
    )
    dfs['Trigger_Ave'].Children.loc[index] = (
            dfs['Trigger_Ave'].Male_child.loc[index] +
            dfs['Trigger_Ave'].Female_child.loc[index]
    )

    # Map the time since last ebola case question from a string to an approximate Timedelta
    t_q1_map = IDDict({
        'last week': pd.Timedelta(days=7),
        '2-3 weeks': pd.Timedelta(days=17, hours=6),
        '3weeks': pd.Timedelta(days=21),
        '4 weeks or more': pd.Timedelta(days=28),
        '4 weeks 0r m0re': pd.Timedelta(days=28),
        '5 weeks or more': pd.Timedelta(days=35),
    })
    dfs['Trigger_Other'].t_q1 = dfs['Trigger_Other'].t_q1.str.strip().str.lower().map(t_q1_map)

    # Map the t_q5 column from a string response to a categorical variable
    t_q5_map = IDDict({
        'very low': 0,
        'low': 1,
        'medium': 2,
        'high': 3,
        'very high': 4,
        'very hig': 4,
    })
    dfs['Trigger_Other'].t_q5 = dfs['Trigger_Other'].t_q5.str.strip().str.lower().map(t_q5_map)

    # Clean up the text based columns
    sheets = ['Trigger_Other', 'Follow_Up_Other']
    str_colz = [
        ['t_q4', 't_q6', 't_q7', 't_q8', 't_q9', 't_q10', 't_q11'],
        ['f_q2', 'f_q3', 'f_q4', 'f_q5', 'f_q6'],
    ]

    for sheet, str_cols in zip(sheets, str_colz):
        for str_col in str_cols:
            map_file = f'../data/column_maps/{sheet}_{str_col}_map.json'
            if not Path(map_file).is_file():
                make_spelling_correction_map(dfs, sheet=sheet, col=str_col)

            with open(map_file) as f:
                str_col_map = IDDict(json.load(f))
            dfs[sheet].loc[:, str_col] = (
                dfs[sheet].loc[:, str_col]
                    .str.lower()
                    .str.strip(' .,\"')
                    .str.replace('  ', ' ')
                    .map(str_col_map)
            )

    # Clean up the location columns
    sheets = ['Follow_Up', 'Trigger_NA', 'Trigger_Ave', 'Trigger_Other', 'Follow_Up_Other']
    loc_cols = ['District', 'Chiefdom', 'Section']

    if not check_location_maps():
        print('Constructing default location mappings.')
        make_location_maps(dfs)

    for loc_col in loc_cols:
        map_file = f'../data/column_maps/{loc_col.lower()}_map.json'
        if verbose:
            print(f'Loading map file: {map_file}')
        with open(map_file) as f:
            loc_col_map = IDDict(json.load(f))
        for sheet in sheets:
            dfs[sheet].loc[:, loc_col] = dfs[sheet].loc[:, loc_col].str.strip().map(loc_col_map)

    return dfs


def make_spelling_correction_map(dfs, sheet, col):
    values = sorted(
        dfs[sheet][col].str.lower().str.strip(' .,\"').str.replace('  ', ' ').dropna().unique()
    )
    with Pool() as pool:
        fixed_values = pool.map(fix_spelling_errors, values)

    with open(f'../data/column_maps/{sheet}_{col}_map.json', 'w') as f:
        json.dump({
            x: y
            for x, y in zip(values, fixed_values)
        },
            f,
            indent=4,
            sort_keys=True,
        )


def make_column_correction_map(dfs, sheet, col):
    values = sorted(dfs[sheet][col].dropna().str.strip().unique())

    with open(f'../data/column_maps/{sheet}_{col}_map.json', 'w') as f:
        json.dump({
            x: y
            for x, y in zip(values, values)
        },
            f,
            indent=4,
            sort_keys=True,
        )


def fix_spelling_errors(sample, threshold=1):
    suggestions = sym_spell.lookup_compound(sample, max_edit_distance=2)

    # Suggestion object attributes:
    #  - term: the corrected string
    #  - distance: the edit distance
    #  - count: Naive Bayes probability of the individual suggestion parts
    suggestion = suggestions[0]
    if suggestion.count > threshold:
        return suggestion.term
    else:
        return sample


def validate_sheet_locations(
        dfs,
        sheet_name,
        data_kind,
        output_path='../data/column_discrepancies',
        verbose=False,
):
    output_path = Path(output_path)
    output_path.mkdir(exist_ok=True, parents=True)

    if verbose:
        print(f'Validating {sheet_name} locations.')

    districts = set(dfs[sheet_name].District.dropna().str.strip().unique())
    district_issues = sorted(districts - set(sierra_leone.districts))
    with open(output_path / f'{data_kind}_{sheet_name}_Districts.json', 'w') as f:
        json.dump(district_issues, f, indent=4)

    chiefdoms = set(dfs[sheet_name].Chiefdom.dropna().str.strip().unique())
    chiefdom_issues = sorted(chiefdoms - set(sierra_leone.chiefdoms))
    with open(output_path / f'{data_kind}_{sheet_name}_Chiefdoms.json', 'w') as f:
        json.dump(chiefdom_issues, f, indent=4)

    sections = set(dfs[sheet_name].Section.dropna().str.strip().unique())
    section_issues = sorted(sections - set(sierra_leone.sections))
    with open(output_path / f'{data_kind}_{sheet_name}_Sections.json', 'w') as f:
        json.dump(section_issues, f, indent=4)

    if verbose:
        print(
            f'{sheet_name} - {data_kind}:'
            f'\n\tDistrict Issues: {len(district_issues)}'
            f'\n\tChiefdom Issues: {len(chiefdom_issues)}'
            f'\n\tSection Issues: {len(section_issues)}\n\n'
        )


def check_location_maps(path='../data/column_maps'):
    return (
            Path(f'{path}/district_map.json').is_file() and
            Path(f'{path}/chiefdom_map.json').is_file() and
            Path(f'{path}/section_map.json').is_file()
    )


def make_location_maps(dfs, sheets=None, output_path='../data/column_maps'):
    """
    Creates a single, unified mapping to clean up the location columns (District,
    Chiefdom, and Section) across all of the sheets that have them.

    Args:
        dfs:
        sheets:
        output_path:
    """
    output_path = Path(output_path)
    output_path.mkdir(exist_ok=True, parents=True)
    sheets = sheets or ['Follow_Up', 'Trigger_NA', 'Trigger_Ave', 'Trigger_Other', 'Follow_Up_Other']
    loc_cols = ['District', 'Chiefdom', 'Section']

    for loc_col in loc_cols:
        mapping = dict()
        for sheet in sheets:
            sheet_map = {
                x: x
                for x in dfs[sheet][loc_col].str.strip().str.replace('  ', ' ').dropna().unique()
            }
            mapping.update(sheet_map)

        with open(f'../data/column_maps/{loc_col.lower()}_map.json', 'w') as f:
            json.dump(
                mapping,
                f,
                indent=4,
                sort_keys=True,
            )


class IDDict(dict):
    """
    pandas.Series.map takes a dictionary and uses it to modify values in the series.
    When a value in the series does not have mapping defined by the dictionary,
    the default behavior is to replace that value with NaN. In order to avoid
    manipulating the raw data more than intended, this dictionary creates an identity
    mapping for missing keys making the map function less destructive.
    """
    def __missing__(self, key):
        return key


if __name__ == '__main__':
    main(**vars(get_parser().parse_args()))
