def x():
    return True


class Dummy:
    pass


print(callable(Dummy))
print(callable(x))
