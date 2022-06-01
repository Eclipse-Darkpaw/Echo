import os
import json


def profile_update(root, files, dicty):
    profiles = dicty
    for file in files:
        with open(root + '\\' + file, 'r') as prof:
            profile = prof.readline().replace('/n', '\n')
        profiles[int(file[0:-8])] = {"profile": profile}
    return profiles

def ref_update(root, files, refs):
    directory = root.split('\\')
    for file in files:
        with open(root + '\\' + file, 'r') as prof:
            ref = prof.read().replace('/n', '\n')
            if len(str(file[:-5])) == 18:
                id = int(file[0:18])
                try:
                    refs[id]['refs'] = {'main': ref}
                except KeyError:
                    refs[id] = {'refs:': {'main': ref}}
            elif len(directory[-1]) == 18:
                refs[int(directory[-1])]['refs'][file[:-4]] = ref
            else:
                continue
    return refs


def update_files():
    dictionary = {}
    for (root, dirs, files) in os.walk('resources'):
        directory = root.split('\\')
        switch = {'profile': profile_update, 'refs': ref_update}
        try:
            dictionary = switch[directory[1]](root, files, dictionary)
        except IndexError:
            continue
        except KeyError:
            continue
    json_object = json.dumps(dictionary, indent=4)
    with open('resources/global_files.json', 'w') as file:
        file.write(json_object)


if __name__ == '__main__':
    update_files()
    