from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
            cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, value) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)

class TransactionModel(BaseModel):
    transaction_id: str
    timestamp: datetime
    merchant: str
    category: str
    amount: float
    currency: str
    type: str
    note: Optional[str] = None

class BankModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    bank_id: str
    balance: float = 0.0
    transactions: List[TransactionModel] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
