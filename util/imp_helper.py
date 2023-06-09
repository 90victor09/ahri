import importlib


def import_class(module_path):
    path_arr = module_path.split('.')
    class_name = path_arr.pop()

    module = importlib.import_module('.'.join(path_arr))
    return getattr(module, class_name)


def create_model(model_name):
    return import_class(f'models.{model_name}')()
