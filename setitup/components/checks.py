import shutil

from setitup.utils.click import Context


def is_installed(cmd: str) -> bool:
    return (shutil.which(cmd) is not None) and not Context.force
