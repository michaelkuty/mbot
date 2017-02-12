
MERGEABLES = (list, tuple, dict)


def merge(a, b):
    """Merge tuples, lists or dictionaries without duplicates
    """
    if isinstance(a, MERGEABLES) \
            and isinstance(b, MERGEABLES):
        # dict update
        if isinstance(a, dict) and isinstance(b, dict):
            a.update(b)
            return a
        # list update
        _a = list(a)
        for x in list(b):
            if x not in _a:
                _a.append(x)
        return _a
    if a and b:
        raise Exception("Cannot merge")
    raise NotImplementedError
