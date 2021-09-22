import os


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


def thread(things, *fns):
    result = things
    for f in fns:
        if things is None:
            return None
        result = f(result)
    return result


def absolute_path(filepath):
    return os.path.abspath(os.path.expanduser(filepath))
