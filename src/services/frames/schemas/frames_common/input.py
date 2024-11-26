from pydantic import BaseModel, NonNegativeInt, PositiveFloat


class FramesBaseInputSchema(BaseModel):
    thickness: PositiveFloat
    height_platband_stands: PositiveFloat
    doorway: PositiveFloat

    # naming data
    number_order: NonNegativeInt | None
    date_order: str | None
    name_client: str | None
    address_order: str | None

    path_folder: str | None
