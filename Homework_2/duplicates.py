import sys
from os import walk, path
from hashlib import sha1 as hasher


def print_duplicates(root_directory):
    block_size = 2 ** 20
    file_hashes = {}
    for current_path, folders, files in walk('.'):
        for file_name in files:
            if file_name[0] in ['.', '~']:
                continue;

            with open(path.join(current_path, file_name), mode='rb') as f:
                my_hasher = hasher()
                block = f.read(block_size)
                while block:
                    my_hasher.update(block)
                    block = f.read(block_size)

                file_hash = my_hasher.hexdigest()
                full_file_name = path.join(current_path, file_name)
                if file_hash not in file_hashes:
                    file_hashes[file_hash] = [full_file_name]
                else:
                    file_hashes[file_hash].append(full_file_name)

    for files_with_hash in file_hashes.values():
        if len(files_with_hash) > 1:
            print(*files_with_hash, sep=':')

def main():
    root_directory = sys.argv[1]
    print_duplicates(root_directory)

if __name__ == '__main__':
    main()
