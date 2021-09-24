import pathlib
import os
from sys import platform


def first(thing):
    if isinstance(thing, list):
        try:
            return thing[0]
        except IndexError:
            return thing
    else:
        return thing


def keep_keys(dict_or_list, keys_to_keep):
    if not dict_or_list:
        return {}
    if isinstance(keys_to_keep, str):
        keys_to_keep = [keys_to_keep]
    if isinstance(dict_or_list, list):
        return [keep_keys(d, keys_to_keep) for d in dict_or_list]
    else:
        return {k: v for k, v in dict_or_list.items() if k in keys_to_keep}


def drop_keys(dict_or_list, keys_to_drop):
    if not dict_or_list:
        return {}
    if isinstance(keys_to_drop, str):
        keys_to_drop = [keys_to_drop]
    if isinstance(dict_or_list, list):
        return [drop_keys(d, keys_to_drop) for d in dict_or_list]
    else:
        return {k: v for k, v in dict_or_list.items() if k not in keys_to_drop}


def drop_falsy(dicts):
    """
    Return a list of dicts having removed keys with falsy values.
    """
    if isinstance(dicts, dict):
        dicts = [dicts]
    return [{k:v for k,v in d.items() if v} for d in dicts]


def thread(things, *fns):
    result = things
    for f in fns:
        if things is None:
            return None
        result = f(result)
    return result


def absolute_path(filepath):
    return os.path.abspath(os.path.expanduser(filepath))


def get_windows_drive_letter(directory):
    """
    In the context of serato libraries, serato does not store a drive letter,
    but does store the file in absolute form. So depending on where the serato
    library is, determines which drive letter the files should use.

    ex. _Serato_ is on E:/, then any tracks should be prefixed with E:/
    """
    return pathlib.Path(directory).drive + "/"
