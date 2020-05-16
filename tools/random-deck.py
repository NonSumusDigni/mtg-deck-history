import argparse
import os
import random
import re


OP_PREFIX = '!'
LIST_OP = f'{OP_PREFIX}list'
NOT_OP = f'{OP_PREFIX}not'


def random_decks(directory, query, count=2, all_=False, chaos=False, ultra_chaos=False, verbose=False):
    all_deck_paths = find_all_deck_paths(directory)
    all_decks = list(filter(bool, map(lambda d: parse_deck(d, verbose), all_deck_paths)))
    decks = filter_decks(all_decks, query)

    if all_:
        return decks
    else:
        return select_decks(decks, count, chaos, ultra_chaos)


deck_file_formats = frozenset(['.cod', '.dec', '.mwdeck'])


def find_all_deck_paths(dir_path, deck_paths=[]):
    for root, directories, files in os.walk(dir_path):
        for directory in directories:
            find_all_deck_paths(directory, deck_paths)

        for file_ in files:
            if os.path.splitext(file_)[-1].lower() in deck_file_formats:
                deck_paths.append(os.path.join(root, file_))

    return deck_paths


def parse_deck(deck_path, verbose):
    try:
        dir_path, full_file_name = os.path.split(deck_path)
        dir_parts = dir_path.split(os.path.sep)
        file_name, _ = os.path.splitext(full_file_name)

        return { **parse_dir_parts(dir_parts), **parse_file_name(file_name), 'file_path': deck_path }
    except Exception as ex:
        if verbose and False:
            print(f'Error while parsing deck ({deck_path}): {ex}')

        return None


def filter_decks(decks, query):
    return list(filter(lambda d: match_query(d, query), decks))


def match_query(deck, query):
    for key, value in query.items():
        if key not in deck:
            return False

        if not val_compare(deck[key], value):
            return False

    return True


def val_compare(deck_val, query_val):
    if type(query_val) is dict:
        if NOT_OP in query_val:
            return not val_compare(deck_val, query_val[NOT_OP])

        if LIST_OP in query_val:
            requires = list(filter(lambda opt: type(opt) == str, query_val[LIST_OP]))
            rejects = list(filter(lambda opt: type(opt) == dict, query_val[LIST_OP]))
            return (len(requires) == 0 or any(map(lambda option: val_compare(deck_val, option), requires))) \
                and (len(rejects) == 0 or all(map(lambda option: val_compare(deck_val, option), rejects)))

    if type(query_val) is str:
        return type(deck_val) is str and query_val.lower() in deck_val.lower()

    return deck_val == query_val


def select_decks(decks, count, chaos, ultra_chaos):
    if len(decks) < count:
        print(f'Cannot choose {count} decks, only found {len(decks)} matching decks')
        return []

    selected_decks = []
    for _ in range(count):
        random_deck = random.choice(decks)
        selected_decks.append(random_deck)
        decks.remove(random_deck)

        if len(selected_decks) == 1:
            if not chaos and not ultra_chaos:
                decks = list(filter(lambda d: match_query(d, {
                    'format': random_deck['format'],
                    'format_epoch': random_deck['format_epoch']
                }), decks))
            elif not ultra_chaos:
                decks = list(filter(lambda d: match_query(d, { 'format': random_deck['format'] }), decks))

            if len(decks) < count - 1:
                print(f'Cannot choose {count} decks, only found {len(decks)} matching decks')
                return [*selected_decks, *decks]

    return selected_decks


def parse_dir_parts(dir_parts):
    tournament, format_epoch, format_ = (list(reversed(dir_parts)))[:3]
    tournament_date, tournament_name = parse_tournament_str(tournament)

    return {
        'tournament_name': tournament_name,
        'tournament_date': tournament_date,
        'format_epoch': format_epoch,
        'format': format_
    }


file_name_regex = re.compile(r'^(\[(?P<deck_tag>.+)\])?\s*(?P<tournament_placement>.+)\.\s*(?P<archetype>.+)\s+-\s+(?P<player>.+)$')


def parse_file_name(file_name):
    match = file_name_regex.match(file_name)
    return {
        'tournament_placement': match.group('tournament_placement'),
        'archetype': match.group('archetype'),
        'player': match.group('player'),
        'tag': match.group('deck_tag')
    }


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
        query['tag'] = as_not('incomplete')

    for key, value in [*requires, *(map(lambda kv: [kv[0], as_not(kv[1])], rejects))]:
        if key in query:
            current_value = query[key]
            if type(current_value) is dict and LIST_OP in current_value:
                current_value[LIST_OP].append(value)
            else:
                query[key] = { LIST_OP: [current_value, value] }
        else:
            query[key] = value

    return query


def pretty_print_deck(deck):
    return '[{format}, {format_epoch}] {archetype} as played by {player} to a {tournament_placement} place finish at {tournament_name} on {tournament_date}'.format(**deck)


def as_not(value):
    return { NOT_OP: value }


def test():
    test_deck = {
        'format': 'Standard',
        'format_epoch': '2000-02-NEM',
        'tournament_date': '2000-03-04',
        'tournament_name': 'Grand Prix Dallas',
        'tournament_placement': '3rd-4th',
        'player': 'Jamie Kennedy (MmmPasta)',
        'archetype': 'Counter-Rebels',
        'colors': 'WU',
    }

    assert match_query(test_deck, { 'format': 'standard' })
    assert match_query(test_deck, { 'format': 'STANDARD' })
    assert match_query(test_deck, { 'format': 'sta' })
    assert not match_query(test_deck, { 'format': 'extended' })

    assert match_query(test_deck, { 'format': { LIST_OP: ['extended', 'standard'] } })
    assert not match_query(test_deck, { 'format': { LIST_OP: ['extended', 'vintage'] } })

    assert not match_query(test_deck, { 'tournament_name': { NOT_OP: 'grand prix' } })
    assert match_query(test_deck, { 'tournament_name': { NOT_OP: 'pro tour' } })

    assert match_query(test_deck, {
        'tournament_name': { LIST_OP: [{ NOT_OP: 'pro tour' }, { NOT_OP: 'mythic championship' }] }
    })
    assert not match_query(test_deck, {
        'tournament_name': { LIST_OP: [{ NOT_OP: 'national' }, { NOT_OP: 'grand prix' }] }
    })

    assert match_query(test_deck, {
        'format': 'standard',
        'tournament_name': { LIST_OP: [{ NOT_OP: 'mythic championship' }, { NOT_OP: 'pro tour' }] },
        'tournament_placement': { LIST_OP: ['1st', '2nd', '3rd', '4th'] }
    })
    assert not match_query(test_deck, {
        'format': 'standard',
        'tournament_name': { LIST_OP: [{ NOT_OP: 'mythic championship' }, { NOT_OP: 'pro tour' }] },
        'tournament_placement': { LIST_OP: ['1st', '2nd', { NOT_OP: 'th' }] }
    })


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Select one or more random decks the collection (searched recursively). Must be run from the root of the git repo (e.g. cd path/to/mtg-deck-history; python tools/random-deck.py)')
    parser.add_argument('directory', nargs='?', default=os.path.curdir, help='The directory to select decks from (default: %(default)s)')
    parser.add_argument('--count', '-c', type=int, default=2, help='Number of decks to return (default: %(default)s)')
    parser.add_argument('--all', '-a', action='store_true', help='Instead of returning random decks, return all decks that match the search (default: %(default)s)')
    parser.add_argument('--require', '-r', nargs=2, action='append', default=[], help='Key pair that decks must match (examples: format standard, format_epoch 2000-02-NEM, tournament_name "pro tour")')
    parser.add_argument('--reject', '-j', nargs=2, action='append', default=[], help='Key pair that decks must NOT match (examples: format standard, format_epoch 2000-02-NEM, tournament_name "pro tour")')
    parser.add_argument('--allow-incomplete', '-i', action='store_true', help='Include incomplete decklists in the pool of decks (default: %(default)s)')
    parser.add_argument('--chaos', '-x', action='store_true', help='Allow decks to come from different epochs (default: %(default)s)')
    parser.add_argument('--ultra-chaos', '-u', action='store_true', help='Allow decks to come from different formats (default: %(default)s)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output (default: %(default)s)')
    parser.add_argument('--test', '-t', action='store_true', help='Run the tests, do nothing else (default: %(default)s')
    args = parser.parse_args()

    if args.test:
        test()
        print('All tests passed!')
    else:
        if args.verbose:
            print(f'args are: {args}\n')

        query = query_from_args(args)

        if args.verbose:
            print(f'query is: {query}\n')

        decks = random_decks(args.directory, query, count=args.count, all_=args.all, chaos=args.chaos, ultra_chaos=args.ultra_chaos, verbose=args.verbose)
        if len(decks) > 0:
            separator = '\n\nVERSUS\n\n' if args.count == 2 and not args.all else '\n'
            print(separator.join(map(pretty_print_deck, decks)))
