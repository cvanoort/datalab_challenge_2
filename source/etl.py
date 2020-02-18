"""
TODO:
 - dfs['Trigger Other'].t_q4: str -> int (?)
"""

import json
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
import pkg_resources
from symspellpy import SymSpell

# Configure a global spell checker
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


def load_smac_data(path='../data/clean/all_paper_data.xlsx'):
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


def clean_smac_data(dfs):
    clean_int_col_map = {'o': 0, 'O': 0, 'nan': 0}
    for i in range(100):
        clean_int_col_map[i] = i

    dfs['Follow Up'].Children = dfs['Follow Up'].Children.map(clean_int_col_map)
    dfs['Follow Up'].r_mc = dfs['Follow Up'].r_mc.map(clean_int_col_map)
    dfs['Follow Up'].r_fa = dfs['Follow Up'].r_fa.map(clean_int_col_map)

    t_q1_map = {
        'last week': pd.Timedelta(days=7),
        '2-3 weeks': pd.Timedelta(days=17, hours=6),
        '3weeks': pd.Timedelta(days=21),
        '4 weeks or more': pd.Timedelta(days=28),
        '4 weeks 0r m0re': pd.Timedelta(days=28),
        '5 weeks or more': pd.Timedelta(days=35),
    }
    dfs['Trigger Other'].t_q1 = dfs['Trigger Other'].t_q1.str.strip().str.lower().map(t_q1_map)

    # What is the position of the champion?
    # Champion is a local who is supposed to lead community response to ebola
    t_q4_map_file = '../data/clean/to_t_q4_map.json'
    if not Path(t_q4_map_file).is_file():
        make_trigger_other_t_q4_map(dfs)

    with open(t_q4_map_file) as f:
        t_q4_map = json.load(f)
    dfs['Trigger Other'].t_q4 = dfs['Trigger Other'].t_q4.str.lower().str.strip().str.replace('  ', ' ').str.strip(
        '.').map(t_q4_map)

    t_q5_map = {
        'very low': 0,
        'low': 1,
        'medium': 2,
        'high': 3,
        'very high': 4,
        'very hig': 4,
    }
    dfs['Trigger Other'].t_q5 = dfs['Trigger Other'].t_q5.str.strip().str.lower().map(t_q5_map)

    return dfs


def make_trigger_other_t_q4_map(dfs, out_file='../data/clean/to_t_q4_map.json'):
    positions = sorted(
        dfs['Trigger Other'].t_q4.str.lower().str.strip().str.replace('  ', ' ').str.strip('.').dropna().unique()
    )
    with Pool() as pool:
        fixed_positions = pool.map(fix_spelling_errors, positions)

    with open(out_file, 'w') as f:
        json.dump({
            x: y
            for x, y in zip(positions, fixed_positions)
        },
            f,
            indent=4,
            sort_keys=True,
        )


def fix_spelling_errors(sample, threshold=10):
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


def main():
    dfs = load_smac_data()
    dfs = clean_smac_data(dfs)

    for label, df in sorted(dfs.items()):
        print(f'{label}:\n{df.dtypes}\n\n')


if __name__ == '__main__':
    main()
