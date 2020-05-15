import argparse
import os
import random
import re


OP_PREFIX = '!'
OR_OP = f'{OP_PREFIX}or'
NOT_OP = f'{OP_PREFIX}not'


def random_decks(directory, query, count=2, all_=False):
    all_deck_paths = find_all_deck_paths(directory)
    all_decks = map(parse_deck, all_deck_paths)
    decks = filter_decks(all_decks, query)

    if all_:
        return decks
    else:
        return select_decks(decks, count)


deck_file_formats = frozenset(['.cod', '.dec', '.mwdeck'])


def find_all_deck_paths(dir_path, deck_paths=[]):
    for root, directories, files in os.walk(dir_path):
        for directory in directories:
            find_all_deck_paths(directory, deck_paths)

        for file_ in files:
            if os.path.splitext(file_)[-1].lower() in deck_file_formats:
                deck_paths.append(os.path.join(root, file_))

    return deck_paths


def parse_deck(deck_path):
    dir_path, full_file_name = os.path.split(deck_path)
    dir_parts = dir_path.split(os.path.sep)
    file_name, _ = os.path.splitext(full_file_name)

    return {
        **parse_dir_parts(dir_parts),
        **parse_file_name(file_name)
    }


def filter_decks(decks, query):
    # TODO
    return decks


def select_decks(decks, count):
    if len(decks) < count:
        print(f'Cannot choose {count} decks, only found {len(decks)} matching decks')
        return []

    selected_decks = []
    for _ in range(count):
        random_deck = random.choice(decks)
        selected_decks.append(random_deck)
        decks.remove(random_deck)

    return selected_decks


def parse_dir_parts(dir_parts):
    tournament, format_epoch, format_ = (list(reversed(dir_parts)))[:3]
    tournament_date, tournament_name = parse_tournament_str(tournament)

    return {
        tournament_name: tournament_name,
        tournament_date: tournament_date,
        format_epoch: format_epoch,
        format: format_
    }


file_name_regex = re.compile(r'^(\[(?P<deck_tags>.+)\])?\s*(?P<tournament_placement>.+)\.\s*(?P<archetype>.+)\s+-\s+(?P<player>.+)$')


def parse_file_name(file_name):
    try:
        match = file_name_regex.match(file_name)
        return {
            tournament_placement: match.group('tournament_placement'),
            archetype: match.group('archetype'),
            player: match.group('player'),
            tags: list(map(lambda x: x.strip().lower(), (match.group('deck_tags') or '').split(',')))
        }
    except e:
        print(f"Error in parse_file_name('{file_name}'): {str(e)}")
        return {}


tournament_regex = re.compile(r'^(?P<tournament_date>[\d-]+)\s+-\s+(?P<tournament_name>.+)$')


def parse_tournament_str(tournament):
    match = tournament_regex.match(tournament)
    return match.group('tournament_date'), match.group('tournament_name')


def query_from_args(args):
    requires = args.require
    rejects = args.reject
    allow_incomplete = args.allow_incomplete

    query = {}

    if not allow_incomplete:
        query['tags'] = as_not('incomplete')

    for key, value in [*requires, *(map(lambda kv: [kv[0], as_not(kv[1])], rejects))]:
        if key in query:
            current_value = query[key]
            if type(current_value) is dict and OR_OP in current_value:
                current_value[OR_OP].append(value)
            else:
                query[key] = { OR_OP: [current_value, value] }
        else:
            query[key] = value

    return query


def pretty_print_deck(deck):
    # TODO
    return str(deck)


def as_not(value):
    return { NOT_OP: value }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Select one or more random decks the collection (searched recursively). Must be run from the root of the git repo (e.g. cd path/to/mtg-deck-history; python tools/random-deck.py)')
    parser.add_argument('directory', nargs='?', default=os.path.curdir, help='The directory to select decks from (default: %(default)s)')
    parser.add_argument('--count', '-c', type=int, default=2, help='Number of decks to return (default: %(default)s)')
    parser.add_argument('--all', '-a', action='store_true', help='Instead of returning random decks, return all decks that match the search (default: %(default)s)')
    parser.add_argument('--require', '-r', nargs=2, action='append', default=[], help='Key pair that decks must match (examples: format standard, format_epoch 2000-02-NEM, tournament_name "pro tour")')
    parser.add_argument('--reject', '-j', nargs=2, action='append', default=[], help='Key pair that decks must NOT match (examples: format standard, format_epoch 2000-02-NEM, tournament_name "pro tour")')
    parser.add_argument('--allow-incomplete', '-i', action='store_true', help='Include incomplete decklists in the pool of decks (default: %(default)s)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output (default: %(default)s)')
    args = parser.parse_args()

    print(f'args are: {args}')

    query = query_from_args(args)

    print(f'query is: {query}')

    #decks = random_decks(args.directory, query={}, count=args.count, all=args.all)
    #if len(decks) > 0:
    #    separator = '\nVERSUS\n' if args.count == 2 and not args.all else '\n\n\n'
    #    print(separator.join(map(pretty_print_deck, indexed_decks)))
