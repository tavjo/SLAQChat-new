from typing import TypedDict, Optional, Any, Annotated, Sequence
# from langgraph.graph import MessagesState
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from typing import List
from langgraph.managed import IsLastStep, RemainingSteps
from langgraph.prebuilt.chat_agent_executor import StructuredResponse

class Column(BaseModel):
    name: str
    type: str
    nullable: bool
    default: Optional[Any]
    json_keys: Optional[List[str]]

class Table(BaseModel):
    name: str
    columns: List[Column]

class DBSchema(BaseModel):
    tables: List[Table] | str


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

class ParsedQuery(TypedDict):
    uid: Optional[str] | Optional[List[str]] 
    sampletype: Optional[str] | Optional[List[str]]
    assay: Optional[str] | Optional[List[str]]
    attribute: Optional[str] | Optional[List[str]]
    terms: Optional[str] | Optional[List[str]]

class ResourceBox(TypedDict):
    sample_metadata: Optional[Metadata] | Optional[List[Metadata]] | Optional[str]
    db_schema: Optional[DBSchema]
    protocolURL: Optional[str]
    sampleURL: Optional[str]
    UIDs: Optional[List[str]]  # You can omit '= None' in TypedDict
    parsed_query: Optional[ParsedQuery]


class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages, ResourceBox]

# New unified state model: separate messages and resources.

class ToolMetadata(TypedDict):
    doc: str
    signature: str

class WorkerState(TypedDict):
    agent: str
    role: str
    toolbox: Optional[dict[str, ToolMetadata]]

class ConversationState(TypedDict):
    messages: List[BaseMessage]
    resources: Optional[ResourceBox]
    available_workers: Optional[list[WorkerState]]
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps
    structured_response: StructuredResponse

class SchemaMapperState(BaseModel):
    relevant_keys: List[str]
    schema_map: str
    justification: str