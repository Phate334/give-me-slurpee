from typing import Optional

from pydantic import BaseModel


class Store711(BaseModel):
    """
    7-11 store address and geo from OpenStreetMap.
    """

    name: str
    address: str
    lat: Optional[float] = None
    lon: Optional[float] = None
