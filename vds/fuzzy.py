"""
Fuzzy matching of strings/names.
"""

import csv
from collections import defaultdict, Counter


def group_by(kv_pairs):
    """Group key-value pairs by key"""
    groups = defaultdict(list)
    for k, v in kv_pairs:
        groups[k].append(v)
    return groups


def ngrams(text, n=3):
    """Return list of text n-grams of size n"""
    return {text[i:i + n].lower() for i in range(len(text) - n + 1)}


def find(query, index):
    """Find best match of query string in n-gram index"""
    sgrams = ngrams(query)
    matches = Counter(sid for ngram in sgrams for sid in index.get(ngram, []))
    return matches.most_common(1)


def create_index(filename):
    """Create n-gram index that maps n-grams to subject ids"""
    sid2name = load_sid2name(filename)
    return group_by((ngram, sid) for sid, name in sid2name for ngram in ngrams(name))


def load_sid2name(filename):
    """Load file that maps subject ids to names"""
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header
        for sid, name in reader:
            yield sid.rjust(6, '0'), name.replace(',', ' ')


if __name__ == '__main__':
    print('running')
    index = create_index('../data/subject_ids.csv')
    while 1:
        query = input('search: ')
        if query == 'q': break
        print('-' * 50)
        match = find(query, index)
        print(match[0] if match else 'NO MATCH')
