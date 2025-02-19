class DataSummarizer {
    summary string @description("The summary of the input message")
    messages Payload @description("The messages in the conversation")
    justification string @description("The justification for your response")
}

class Navigator {
    agent Agent @description("The current agent in the conversation")
    next_tool string @description("The next tool to use from the agent's toolbox")
    tool_args string[] @description("The arguments to pass to the tool")
    justification string @description("The justification for choosing the next tool")
}

class Responder {
    Next_worker Agent @description("The next worker to call")
    justification string @description("The justification for choosing the next worker")
}

class ResponseFormatter {
    formattedResponse string @description("Formatted response for the user")
    name string @description("The name of the current worker : response_formatter")
    messages Payload @description("Conversation history and context")
    justification string @description("The justification for your response")
}

class Supervisor {
    Next_worker Agent @description("The next worker to call")
    justification string @description("The justification for choosing the next worker")
}

class Metadata {
    AntibodyParent string?
    BioSampleAccession string?
    BiosafetyLevel string?
    Catalog string?
    CellCount string?
    CellLine string?
    CellLineage string?
    Checksum_PrimaryData string?
    Checksum_PrimaryType string?
    CompensationFCSParent string?
    Concentration string?
    ConcentrationUnits string?
    File_PrimaryData string?
    Fixation string?
    Fixative string?
    FlowAmount string?
    FlowAmountUnits string?
    FMO string?
    Genotype string?
    Instrument string?
    InstrumentUser string?
    Link_PrimaryData string?
    Media string?
    Name string?
    Notes string?
    Parent string?
    PassageNum string?
    Path_PrimaryData string?
    Phenotype string?
    Protocol string?
    Protocol_Stimulation string?
    Protocol_Treatment string?
    Publish_uri string?
    QC string?
    QC_notes string?
    ReagenCatalogNum string?
    Reagent string?
    ReagentBrand string?
    ReagentManufacturer string?
    Reference string?
    Repository string?
    RepositoryID string?
    Scientist string?
    SEEKSubmissionDate string?
    SampleCreationDate string?
    Software string?
    Source string?
    SourceFacility string?
    Species string?
    Stain string?
    StorageLocation string?
    StorageSite string?
    StorageTemperature string?
    StorageTemperatureUnits string?
    StorageType string?
    Stimulation string?
    Timepoint string?
    TotalProtein string?
    TotalProteinUnits string?
    Treatment1 string?
    Treatment1Dose string?
    Treatment1DoseUnits string?
    Treatment1Reference string?
    Treatment2 string?
    Treatment2Dose string?
    Treatment2DoseUnits string?
    Treatment2Reference string?
    TreatmentDoseTime string?
    TreatmentRoute string?
    TreatmentTimeUnits string?
    TreatmentType string?
    Type string?
    UID string?
    ValidationMethod string?
    ValidationQuality string?
    Vendor string?
}

class Payload {
    system_message string @description("The system message")
    user_query string @description("The user message")
    aggregatedMessages string[]? @description("The aggregated messages in the conversation")
    resource ResourceBox? @description("The resources available to the agent")
}

class Agent {
    agent string @description("The name of the agent")
    role string @description("The role of the agent")
    toolbox map<string, ToolMetadata>? @description("The toolbox of the agent")
}

class Validator {
    name string @description("The name of the current agent : validator")
    Valid bool @description("Whether the response is valid")
    Clarifying_Question string? @description("A clarifying question to the user if Valid is false")
    justification string @description("The justification for your response")
    response Payload @description("same as inputMessage")
}

class ToolMetadata {
    doc string @description("The documentation of the tool")
    signature string @description("The signature of the tool")
}

class Table {
    name string @description("The name of the table")
    columns Column[] @description("The columns in the table")
}

class Column {
    name string @description("The name of the column")
    type string @description("The type of the column")
    nullable bool @description("Whether the column can be null")
    default string? @description("The default value of the column")
    json_keys string[]? @description("The keys in the JSON column")
}

class Schema {
    tables Table[] @description("The relevant tables in the database")
}

class SchemaMapper {
    name string @description("The name of the agent: schema_mapper")
    schema_map Schema @description("The mapped schema of the database based on the user query")
    pseudo_query string @description("The proposed query based on schema mapping")
    justification string @description("The justification for the mapping and proposed query")
}

class ResourceBox {
    sample_metadata Metadata[]? @description("Sample metadata")
    protocolUrl string? @description("Protocol download URL i.e.: https://nextseek.mit.edu/seek/sop/uid=<protocol_uid>")
    sampleUrl string? @description("Sample URL i.e.: https://nextseek.mit.edu/seek/sampletree/uid=<sample_uid>")
    UIDs string[]? @description("List of UIDs")
    db_schema Schema? @description("A complete or partial schema of the database")
}