def create_model(klass, src):
    src_dict = vars(src)

    kwargs = {
        k: v for k, v in src_dict.items() if k in getattr(klass, "__annotations__", {})
    }

    return klass(**kwargs)


def common_kwargs(klass, src: dict, exclude=[]):
    kwargs = {
        k: v
        for k, v in src.items()
        if k not in exclude and k in getattr(klass, "__annotations__", {})
    }
    return kwargs
