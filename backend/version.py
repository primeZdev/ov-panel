version = (
    open("pyproject.toml", "r", encoding="utf-8")
    .read()
    .split('version = "')[1]
    .split('"')[0]
)
__version__ = version
