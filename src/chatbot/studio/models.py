from typing import Optional, Any#, Annotated, Sequence, TypedDict
# from langgraph.graph import MessagesState
from langchain_core.messages import BaseMessage
# from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing import List, Union, Dict, Generic, TypeVar, Optional
# from langgraph.managed import IsLastStep, RemainingSteps
# from langgraph.prebuilt.chat_agent_executor import StructuredResponse
from datetime import datetime, timezone
from backend.Tools.schemas import UpdatePipelineMetadata

class Column(BaseModel):
    name: str
    type: str
    nullable: bool
    default: Optional[str] = None
    json_keys: Optional[List[str]] = None

class Table(BaseModel):
    name: str
    columns: List["Column"]

class DBSchema(BaseModel):
    tables: Union[List["Table"], str]


class Message(BaseModel):
    name: str = Field(..., description="The name of the sender")
    message: str = Field(..., description="The message content")
    role: str = Field(..., description="The role of the sender (i.e. user, assistant)")

class Metadata(BaseModel):
    UID: str
    Name: Optional[Union[str, int]] = None
    Link_PrimaryData: Optional[str] = None
    # Allow arbitrary additional fields
    class Config:
        extra = "allow"
        
    def __init__(self, **data):
        super().__init__(**data)

class ParsedQuery(BaseModel):
    uid: Union[Optional[List[str]], str] = None
    sampletype: Union[Optional[List[str]], str] = None
    assay: Union[Optional[List[str]], str] = None
    attribute: Union[Optional[List[str]], str] = None
    terms: Union[Optional[List[str]], str] = None

class SampleTypeAttributes(BaseModel):
    sampletype: str
    st_description: str
    attributes: List[str]

class ResourceBox(BaseModel):
    sample_metadata: Union[Optional["Metadata"], Union[Optional[List["Metadata"]], str]] = None
    protocolURL: Optional[str] = None
    sampleURL: Optional[str] = None
    UIDs: Optional[List[str]] = None
    db_schema: Optional["DBSchema"] = None
    parsed_query: Optional["ParsedQuery"] = None
    st_attributes: Union[Optional[List["SampleTypeAttributes"]], "SampleTypeAttributes"] = None
    update_info: Optional["UpdatePipelineMetadata"] = None


# New unified state model: separate messages and resources.

class ToolMetadata(BaseModel):
    doc: str
    signature: str

class WorkerState(BaseModel):
    agent: str
    role: str
    toolbox: Optional[Dict[str, "ToolMetadata"]] = None

class InputCSV(BaseModel):
    file_id: str
    content: str  # Base64-encoded string representing the CSV file content
    timestamp: str
    session_id: str

class ConversationState(BaseModel):
    messages: Optional[List[BaseMessage]] = []
    session_id: str = Field(..., description="Unique session identifier")
    version: int = Field(1, description="State version for synchronization")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resources: Optional[ResourceBox] = None
    available_workers: Optional[list[WorkerState]] = None
    last_worker: str = "user"
    file_data: Optional["InputCSV"] = Field(None, description="File content and metadata if the user has uploaded an input file.")


class SchemaMapperState(BaseModel):
    relevant_keys: Optional[List[str]] = None
    schema_map: "DBSchema"
    justification: str
    explanation: str

class DeltaMessage(BaseModel):
    session_id: Optional[str] = None
    timestamp: Optional[str] = None
    new_message:str
    version: Optional[int] = None

class ToolResponse(BaseModel):
    result: Optional[Any] = None
    response: Optional[str] = None
    agent: Optional[str] = None
    justification: Optional[str] = None
    explanation: Optional[str] = None

class Payload(BaseModel):
    # system_message: str
    user_query: str
    aggregatedMessages: List["Message"]
    resource: Optional["ResourceBox"] = None
    last_worker: str = "user"

