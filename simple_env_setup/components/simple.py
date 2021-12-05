def run_shell(cmd: str) -> str:
    log_start(cmd)
    if environ.get("ENV_SETUP_DRY_RUN"):
        log = ""
        status = None
    else:
        proc = popen(cmd)
        log = proc.read()
        status = proc.close()
    if status is None:
        log_done()
        return log
    else:
        log_error(log)


T = TypeVar("T")
P = ParamSpec("P")


def run_python(fn: Callable[P, T]) -> Callable[Concatenate[str, P], T]:
    @ wraps(fn)
    def wrapped(name: str, *args: P.args, **kwargs: P.kwargs) -> T:
        log_start(name)
        try:
            out = fn(*args, **kwargs)
            log_done()
            return out
        except Exception as e:
            log_error(str(e))
    return wrapped
