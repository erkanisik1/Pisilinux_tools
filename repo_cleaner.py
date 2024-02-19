#!/usr/bin/env python3

"""PISI Repository Cleaner.

This script removes old PISI packages by taking only two positional arguments.
First one is the path to the PISI repository and second one is the number of
package versions to keep in the repository. (Latest versions will be kept.)

Example:
    This script can easily be run by providing two positional arguments directory and count.

        $ pisi_repository_cleaner.py /path/to/repository 3

Attributes:
    directory (str): Path to the PISI repository.
    count (int): Number of package versions to keep.

"""

import os
import argparse
#from pkg_resources import parse_version
from packaging.version import parse as parse_version
import datetime

DEBUG = 'debug'
VERBOSE = 'verbose'


def print_message(message, message_type):
    if message_type == DEBUG and args.debug or message_type == VERBOSE and args.verbose:
        print(message)


def scan_repository(directory: str) -> list:
    """
    Finds all *.pisi files under the directory.

    Args:
        directory (str): Path to PISI repository.

    Returns:
        list: A list of tuples created by *.pisi file root and file name.

    Examples:
        >>> scan_repository('/path/to/repository')
        [
            ('/path/to/repository/f/firefox/', 'firefox-70.0-1-p2-x86_64.pisi'),
            ('/path/to/repository/s/spotify/', 'spotify-1.1.10.546-15-p2-x86_64.pisi'),
            ...
        ]

    """
    print_message('Started scanning files in repository directory.', VERBOSE)
    pisi_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.pisi'):
                print_message('Found %s in %s.' % (file, root), DEBUG)
                pisi_files.append((root, file))
    return pisi_files


def parse_packages(pisi_files: list) -> dict:
    """
    Parses *.pisi file names and generates dictionaries for packages.

    Args:
        pisi_files (list): A list of tuples which have file root and file name in it.

    Returns:
        dict: A dictionary that contains package name as key and other meta data as value in another dictionary.

    Examples:
        >>> parse_packages([('/path/to/repository/f/firefox/', 'firefox-70.0-1-p2-x86_64.pisi'), ('/path/to/repository/s/spotify/', 'spotify-1.1.10.546-15-p2-x86_64.pisi'),])
        {
            'firefox': {
                'path': '/path/to/repository/f/firefox/',
                'pisi_version': 'p2',
                'arch': 'x86_64',
                'versions': [('70', '0', '1')]
            },
            'spotify': {
                'path': '/path/to/repository/s/spotify/',
                'pisi_version': 'p2',
                'arch': 'x86_64',
                'versions': [('1', '1', '10', '546', '15')]
            }
        }

    """
    print_message('Started parsing PISI files.', VERBOSE)
    packages = {}
    current_datetime = datetime.datetime.now()
    error_log_file = "repo_cleaner_error_log_{}.txt".format(current_datetime.strftime("%Y%m%d_%H%M%S"))

    for path, pisi_file in pisi_files:
        # Remove file extension.
        package_name_without_extension = pisi_file.split('.pisi')[0]
        # Parse file name by splitting last 4 dash (-)
        package_name, version, revision, pisi_version, arch = package_name_without_extension.rsplit('-', 4)
        # Python has a feature to sort list of tuples so that we create tuples from versions by splitting dots (.)
        version_tuple = (*version.split('.'), revision)
        
        try:
            comparable_version = parse_version('.'.join(version_tuple))

            print_message('Parsed %s. Package name: %s, version: %s, revision: %s, pisi version: %s, arch: %s.' %
                        (pisi_file, package_name, version, revision, pisi_version, arch), DEBUG)

            # Merge all package data in a dictionary.
            package = packages.get(package_name, {})
            versions = package.get('versions', [])
            versions.append({'path': path, 'version': version_tuple, 'comparable_version': comparable_version})
            package.update({
                'pisi_version': pisi_version,
                'arch': arch,
                'versions': versions
            })
            packages.update({package_name: package})

        except Exception as e:
            # Hatalı sürüm numarasını error_log_file dosyasına yaz
            with open(error_log_file, 'a') as f:
                f.write("Hata: {} dosyasında '{}' sürüm numarası işlenirken bir hata oluştu. Hata mesajı: {}\n".format(pisi_file, version, str(e)))
            continue  # Hatalı sürüm numarası ile ilgili işlemi pas geç ve bir sonraki dosyaya geç

    return packages


def find_redundant(packages: dict) -> list:
    """
    Finds unwanted packages.

    Args:
        packages: Package dict.

    Returns:
        list: List of file paths to remove.

    """
    print_message('Started finding redundant PISI files.', VERBOSE)
    old_packages = []
    for name, meta in packages.items():
        versions = sorted(meta['versions'], key=lambda x: x.get('comparable_version'), reverse=True)[args.count:]
        for version in versions:
            pisi_file = '{name}-{version}-{revision}-{pisi_version}-{arch}.pisi'.format(
                name=name,
                version='.'.join(version['version'][:-1]),
                revision=version['version'][-1],
                pisi_version=meta['pisi_version'],
                arch=meta['arch'],
            )
            path_to_pisi_file = os.path.join(version['path'], pisi_file)

            print_message('Found redundant package %s.' % path_to_pisi_file, DEBUG)

            old_packages.append(path_to_pisi_file)
    return old_packages


def remove_excess(old_packages: list):
    """
    Removes files in the list.

    Args:
        old_packages (list): List of file names.

    """
    print_message('Started removing redundant PISI files.', VERBOSE)
    for package in old_packages:
        print_message('Removing %s.' % package, DEBUG)
        os.remove(package)


def yes_no_prompt(message: str) -> bool:
    """
    Yes/No prompt to be sure that the user really wants to continue what he/she wants.

    Args:
        message (str): The message that will be prompted to the user.

    Returns:
        bool: True if the user enters 'y', false if enters 'N' or empty.

    """
    while True:
        answer = input(message + ' [y/N]: ')
        if len(answer) == 0:
            return False
        elif len(answer) > 0 and answer[0].lower() in ('y', 'n'):
            return answer[0].lower() == 'y'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Clean Pisi repositories by removing older *.pisi files.")
    parser.add_argument("directory", type=str, help="Pisi repository directory")
    parser.add_argument("count", type=int, help="Number of packages to keep in repository.")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()

    if args.count == 0:
        if not yes_no_prompt('Entering 0 (zero) as count will cause all PISI packages to be '
                             'removed from the directory. Do you really want to continue?'):
            print('Good decision! Exiting.')
            exit(0)

    # Check if the directory exists.
    if not os.path.exists(args.directory):
        print('%s does not exist.' % args.directory)
        exit(-1)
    # Check if the directory is really a directory.
    elif not os.path.isdir(args.directory):
        print('%s is not a directory.' % args.directory)
        exit(-2)

    pisi_files = scan_repository(args.directory)
    # Check if there is any PISI file found.
    if not pisi_files:
        print('Could not find any file ending with .pisi in %s. Exiting.' % args.directory)
        exit(1)
    packages = parse_packages(pisi_files)
    if not packages:
        print('Something is wrong. Could not parse any package from *.pisi files. Exiting.')
        exit(-3)

    redundant_packages = find_redundant(packages)

    # Check if there is any redundant package.
    if not redundant_packages:
        print('There is no redundant package. Repository is clean. The world is a much better place now! :)')
        exit(0)

    # Check if the user really wants to remove the packages.
    if yes_no_prompt('%s redundant packages found. Do you really want to remove them?' % len(redundant_packages)):
        remove_excess(redundant_packages)