from pydantic import BaseModel, Field

# --- Pydantic Models for Data Validation ---
class StartRequest(BaseModel):
    product_name: str = Field(
        ...,
        description="The name of the product to search for.",
        examples=["Sony WH-1000XM5 headphones"],
    )

class StartResponse(BaseModel):
    result: str