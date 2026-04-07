try:
    from .._version import (  # ty: ignore[unresolved-import]
        __version__,
        __version_tuple__,
    )

except ModuleNotFoundError:
    from importlib.metadata import PackageNotFoundError, version

    try:
        _v = version("apkit")
        __version__ = _v
        __version_tuple__ = tuple(int(x) for x in _v.split(".") if x.isdigit())
    except PackageNotFoundError:
        __version__ = "0.0.0"
        __version_tuple__ = (0, 0, 0)
