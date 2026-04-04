def create_model(klass, src):
    src_dict = vars(src)

    kwargs = {
        k: v
        for k, v in src_dict.items()
        if k in getattr(klass, "__annotations__", {})
    }

    return klass(**kwargs)

