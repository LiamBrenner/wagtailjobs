from wagtailjobs.models import JOBINDEX_MODEL_CLASSES


def jobindex(cls):
    JOBINDEX_MODEL_CLASSES.append(cls)
    return cls
