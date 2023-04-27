

def import_class(module_path):
    path_arr = module_path.split('.')
    class_name = path_arr.pop()

    module = __import__('.'.join(path_arr), class_name)
    return getattr(module, class_name)
