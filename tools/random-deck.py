import argparse
import os
import random


deck_file_formats = frozenset(['.cod', '.dec', '.mwdeck'])


def random_decks(directory=os.path.curdir, count=2, requires=[], rejects=[], allow_incomplete=False):
    deck_files = filter_deck_files(find_all_deck_files(directory), requires, rejects, allow_incomplete)

    if len(deck_files) < count:
        print(f'Cannot choose {count} decks, found {len(deck_files)}')
        return []

    selected_decks = []

    for _ in range(count):
        random_deck = random.choice(deck_files)
        selected_decks.append(random_deck)
        deck_files.remove(random_deck)

    return selected_decks


def filter_deck_files(deck_files, requires, rejects, allow_incomplete):
    if not allow_incomplete:
        rejects.append('[INCOMPLETE]')

    lower_requires = list(map(lambda x: x.lower(), requires))
    lower_rejects = list(map(lambda x: x.lower(), rejects))


    def apply_filters(deck_file, requires=lower_requires, rejects=lower_rejects):
        lower_deck_file = deck_file.lower()

        for require_str in requires:
            if require_str not in lower_deck_file:
                return False

        for reject_str in rejects:
            if reject_str in lower_deck_file:
                return False

        return True


    return list(filter(apply_filters, deck_files))


def find_all_deck_files(dir_path, deck_files=[]):
    for root, directories, files in os.walk(dir_path):
        for directory in directories:
            find_all_deck_files(directory, deck_files)

        for file_ in files:
            if os.path.splitext(file_)[-1].lower() in deck_file_formats:
                deck_files.append(os.path.join(root, file_))

    return deck_files


def add_indices(decks):
    i = 0
    indexed_decks = []

    for deck in decks:
        i += 1
        indexed_decks.append(f'{i}. {deck}')

    return indexed_decks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Select one or more random decks from directory (searched recursively)')
    parser.add_argument('--count', '-c', type=int, default=2, help='Number of decks to return')
    parser.add_argument('--require', '-r', action='append', default=[], help='Decks must contain string (examples: standard, vintage, 2001, 1st)')
    parser.add_argument('--reject', '-j', action='append', default=[], help='Decks must NOT contain string (examples: standard, vintage, 2001, 1st)')
    parser.add_argument('--allow-incomplete', '-i', action='store_true', help='Include incomplete decklists in the pool of decks')
    parser.add_argument('directory', nargs='?', default=os.path.curdir, help='The directory to select decks from (defaults to current directory)')
    args = parser.parse_args()

    print(args)

    decks = random_decks(args.directory, args.count, args.require, args.reject, args.allow_incomplete)
    if len(decks) > 0:
        print('\n'.join(add_indices(decks)))
