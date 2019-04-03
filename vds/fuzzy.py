"""
Fuzzy matching of strings/names.
"""

import csv
from collections import defaultdict, Counter


def group_by(kv_pairs):
    groups = defaultdict(list)
    for k, v in kv_pairs:
        groups[k].append(v)
    return groups


def ngrams(text, n=3):
    return {text[i:i + n].lower() for i in range(len(text) - n + 1)}


def create_index(filename):
    sid2name = load_sid2name(filename)
    return group_by((ngram, sid) for sid, name in sid2name for ngram in ngrams(name))


def find(search_str, index):
    sgrams = ngrams(search_str)
    matches = Counter(sid for ngram in sgrams for sid in index.get(ngram, []))
    return matches.most_common(1)


def load_sid2name(filename):
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header
        for sid, name in reader:
            yield sid.rjust(6, '0'), name.replace(',', ' ')


def run():
    for sid, name in load_sid2name('examples/subject_ids.csv'):
        print(sid, name)


if __name__ == '__main__':
    print('running')
    index = create_index('examples/subject_ids.csv')
    while 1:
        search_str = input('search: ')
        if search_str == 'q': break
        print('-' * 50)
        match = find(search_str, index)
        if match:
            print(match[0])
