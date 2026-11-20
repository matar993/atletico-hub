from pydantic import BaseModel, ConfigDict


class RequestModel(BaseModel):
    """Base of every request body: a field the route does not declare answers 422."""

    model_config = ConfigDict(extra="forbid")
