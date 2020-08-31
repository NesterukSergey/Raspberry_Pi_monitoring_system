from pathlib import Path


def list_dirs(path):
    p = Path(path).glob('**/*')
    files = [x for x in p if x.is_file()]
    return files
