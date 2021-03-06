import argparse
import os
import xml.etree.ElementTree as ET


def convert_dir(dir_path, log_prefix='', dry_run=False, delete=False):
    for root, dirs, files in os.walk(dir_path):
        for dir in dirs:
            convert_dir(dir)

        for file in files:
            if file.endswith('.cod'):
                cod_file_name = os.path.join(root, file)

                file_name_part = cod_file_name[:-4]
                dec_file_name = '{}.dec'.format(file_name_part)

                if not os.path.isfile(dec_file_name):
                    print('{}Converting file {}'.format(log_prefix, cod_file_name))
                    dec_file_contents = convert(ET.parse(cod_file_name).getroot())
                    print('{}Writing file {}'.format(log_prefix, dec_file_name))
                    if not args.dry:
                        with open(dec_file_name, 'w') as f:
                            f.write(dec_file_contents)

                if args.delete:
                    print('{}Deleting file {}'.format(log_prefix, cod_file_name))
                    if not args.dry:
                        os.remove(cod_file_name)
    

def convert(xml_root):
    output_lines = []
    for zone in xml_root.iter('zone'):
        zone_name = zone.get('name')
        prefix = 'SB: ' if zone_name != 'main' else ''
        for card in zone.iter('card'):
            card_count = card.get('number')
            card_name = card.get('name')
            output_lines.append('{}{} {}'.format(prefix, card_count, card_name))

    return '\n'.join(output_lines) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert all .cod files to .dec files recursively from the current directory.')
    parser.add_argument('--delete', '-d', action='store_true', help='Also delete the .cod files after converting')
    parser.add_argument('--dry', action='store_true', help="Don't write or delete any files, just print intentions")
    args = parser.parse_args()

    log_prefix = '[DRY RUN] ' if args.dry else ''

    convert_dir(os.path.curdir, log_prefix=log_prefix, dry_run=args.dry, delete=args.delete)

