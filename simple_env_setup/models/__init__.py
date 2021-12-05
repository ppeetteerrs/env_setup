from pydantic import BaseModel


class Model(BaseModel):
    def __repr__(self) -> str:
        return self.__str__()
