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

class Metadata(BaseModel):
    AntibodyParent: Optional[str] = None
    BioSampleAccession: Optional[str] = None
    BiosafetyLevel: Optional[str] = None
    Catalog: Optional[str] = None
    CellCount: Optional[str] = None
    CellLine: Optional[str] = None
    CellLineage: Optional[str] = None
    Checksum_PrimaryData: Optional[str] = None
    Checksum_PrimaryType: Optional[str] = None
    Cohort: Optional[str] = None
    CompensationFCSParent: Optional[str] = None
    Concentration: Optional[str] = None
    ConcentrationUnits: Optional[str] = None
    File_PrimaryData: Optional[str] = None
    Fixation: Optional[str] = None
    Fixative: Optional[str] = None
    FlowAmount: Optional[str] = None
    FlowAmountUnits: Optional[str] = None
    FMO: Optional[str] = None
    Genotype: Optional[str] = None
    Instrument: Optional[str] = None
    InstrumentUser: Optional[str] = None
    Link_PrimaryData: Optional[str] = None
    Media: Optional[str] = None
    Name: Optional[str] = None
    Notes: Optional[str] = None
    Parent: Optional[str] = None
    PassageNum: Optional[str] = None
    Path_PrimaryData: Optional[str] = None
    Phenotype: Optional[str] = None
    Protocol: Optional[str] = None
    Protocol_Stimulation: Optional[str] = None
    Protocol_Treatment: Optional[str] = None
    Publish_uri: Optional[str] = None
    QC: Optional[str] = None
    QC_notes: Optional[str] = None
    ReagenCatalogNum: Optional[str] = None
    Reagent: Optional[str] = None
    ReagentBrand: Optional[str] = None
    ReagentManufacturer: Optional[str] = None
    Reference: Optional[str] = None
    Repository: Optional[str] = None
    RepositoryID: Optional[str] = None
    Scientist: Optional[str] = None
    SEEKSubmissionDate: Optional[str] = None
    SampleCreationDate: Optional[str] = None
    Software: Optional[str] = None
    Source: Optional[str] = None
    SourceFacility: Optional[str] = None
    Species: Optional[str] = None
    Stain: Optional[str] = None
    Stimulation: Optional[str] = None
    StorageLocation: Optional[str] = None
    StorageSite: Optional[str] = None
    StorageTemperature: Optional[str] = None
    StorageTemperatureUnits: Optional[str] = None
    StorageType: Optional[str] = None
    Study: Optional[str] = None
    Timepoint: Optional[str] = None
    TotalProtein: Optional[str] = None
    TotalProteinUnits: Optional[str] = None
    Treatment1: Optional[str] = None
    Treatment1Dose: Optional[str] = None
    Treatment1DoseUnits: Optional[str] = None
    Treatment1Reference: Optional[str] = None
    Treatment2: Optional[str] = None
    Treatment2Dose: Optional[str] = None
    Treatment2DoseUnits: Optional[str] = None
    Treatment2Reference: Optional[str] = None
    TreatmentDoseTime: Optional[str] = None
    TreatmentRoute: Optional[str] = None
    TreatmentTimeUnits: Optional[str] = None
    TreatmentType: Optional[str] = None
    Type: Optional[str] = None
    UID: Optional[str] = None
    ValidationMethod: Optional[str] = None
    ValidationQuality: Optional[str] = None
    Vendor: Optional[str] = None

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

class ConversationState(BaseModel):
    messages: List[BaseMessage]
    session_id: str = Field(..., description="Unique session identifier")
    version: int = Field(1, description="State version for synchronization")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resources: Optional[ResourceBox] = None
    available_workers: Optional[list[WorkerState]] = None


class SchemaMapperState(BaseModel):
    relevant_keys: Optional[List[str]] = None
    schema_map: "DBSchema"
    justification: str
    explanation: str

class DeltaMessage(BaseModel):
    session_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    new_message:str
    version: Optional[int] = None

class ToolResponse(BaseModel):
    result: Optional[Any] = None
    response: Optional[str] = None
    agent: Optional[str] = None
    justification: Optional[str] = None
    explanation: Optional[str] = None

class Payload(BaseModel):
    system_message: str
    user_query: str
    aggregatedMessages: Optional[List[str]] = None
    resource: Optional["ResourceBox"] = None