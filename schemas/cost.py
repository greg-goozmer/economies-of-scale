from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CostRead(BaseModel):
    cost_id: int
    cost_name: str
    cost_description: str | None
    cost_status: str
    cost_image_url: str
    cost_video_url: str
    cost_behavior: str | None
    cost_code: int | None
    cost_created_at: datetime
    cost_creator_id: int
    cost_formed_at: datetime | None
    like_count: int
    is_owner: Literal[0, 1]
    is_liked: Literal[0, 1]


class CostPublish(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cost_description: str = Field(min_length=1, max_length=500)
    cost_behavior: Literal["fixed", "variable"]
    cost_code: int = Field(ge=0)


class CostLikeChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_liked: Literal[0, 1]


class CostLikeRead(BaseModel):
    cost_id: int
    is_liked: Literal[0, 1]
    like_count: int
