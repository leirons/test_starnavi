from typing import Union

from pydantic import BaseModel


class CurrentUser(BaseModel):
    id: Union[int, None]
