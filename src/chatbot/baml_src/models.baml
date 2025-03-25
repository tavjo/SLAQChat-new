class DataSummarizer {
    summary string @description("The summary of the input message")
    explanation string @description("The explanation for your response (how)")
    justification string @description("The justification for your response (why)")
}

class ToolArgs {
    json_keys string?|string[]? @description("json_metadata key(s) for the attribute(s) to search")
    terms string[]? @description("terms to search for in the database")
    uid string?|string[]? @description("exact uid of each sample provided by the user")
    sample_type string[]? @description("specific sample type(s) to pass to the tool")
}

class Navigator {
    agent Agent @description("The current agent in the conversation")
    explanation string @description("The description for choosing the next tool and tool arguments (how)")
    next_tool string @description("The next tool to use from the agent's toolbox")
    tool_args ToolArgs @description("The arguments to pass to the tool")
    justification string @description("The justification for choosing the next tool (why)")
}

class Responder {
    Next_worker Agent @description("The next worker to call")
    explanation string @description("The explanation for choosing the next worker (how)")
    justification string @description("The justification for choosing the next worker (why)")
}

class ResponseFormatter {
    formattedResponse string @description("Formatted response for the user")
    name string @description("The name of the current worker : response_formatter")
    explanation string @description("The explanation for your response (how)")
    justification string @description("The justification for your response (why)")
}

class Supervisor {
    Next_worker Agent @description("The next worker to call")
    explanation string @description("The explanation for choosing the next worker (how)")
    justification string @description("The justification for choosing the next worker (why)")
}

class Metadata {
    Link_PrimaryData string?
    Name string? | int?
    UID string
    @@dynamic // allows adding fields dynamically at runtime
}

class Messages {
    name string @description("The name of the sender")
    message string @description("The message content")
    role string @description("The role of the sender (i.e. user, assistant)")
}

class Payload {
    // system_message string @description("The system message")
    user_query string @description("The user message")
    aggregatedMessages Messages[] @description("The aggregated messages in the conversation")
    resource ResourceBox? @description("The resources available to the agent")
    last_worker string @description("The last worker that processed the message")
}

class Agent {
    agent string @description("The name of the agent")
    role string @description("The role of the agent")
    toolbox map<string, ToolMetadata>? @description("The toolbox of the agent")
}

class Validator {
    name string @description("The name of the current agent : validator")
    explanation string @description("The explanation for your response (how)")
    Valid bool @description("Whether the response is valid")
    response string? @description("same as inputMessage")
    error string? @description("The error message if the response contains an error")
    Clarifying_Question string? @description("A clarifying question to the user if Valid is false")
    justification string @description("The justification for your response (why)")
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

class DBSchema {
    tables Table[] @description("The relevant tables in the database")
}

class SchemaMapper {
    name string @description("The name of the agent: schema_mapper")
    relevant_keys string[] @description("The relevant keys in the database")
    schema_map DBSchema @description("The mapped schema of the database based on the user query")
    justification string @description("The justification for the mapping and proposed query")
    explanation string @description("The explanation for the mapping")
}

class SampleTypeAttributes {
    sampletype string @description("The sample type i.e. MUS, TIS, CEL")
    st_description string @description("The description of the sample type")
    attributes string[] @description("The attributes of the sample type")
}

class UpdatePipelineMetadata{
    success bool @description("Whether the update was successful")
    logs string[] @description("The logs from running the update pipeline")
    errors string[]? @description("The errors from running the update pipeline")
    stats map<string, int>? @description("The stats from running the update pipeline")
}

class ResourceBox {
    sample_metadata Metadata? | Metadata[]? | string? @description("Sample metadata")
    protocolURL string? @description("Protocol download URL i.e.: https://nextseek.mit.edu/seek/sop/uid=<protocol_uid>")
    sampleURL string? @description("Sample URL i.e.: https://nextseek.mit.edu/seek/sampletree/uid=<sample_uid>")
    UIDs string[]? @description("List of UIDs")
    db_schema DBSchema? @description("A complete or partial schema of the database")
    parsed_query ParsedQuery? @description("The parsed user query")
    st_attributes SampleTypeAttributes[]? | SampleTypeAttributes? @description("The sample type attributes")
    update_info UpdatePipelineMetadata? @description("The update information")
}

class ParsedQuery {
    uid string[]? | string? @description("extracted UIDs of the samples from the user query")
    sampletype string[]? | string? @description("extracted sample type from the user query i.e. mouse, tissue, cell line etc.")
    assay string[]? | string? @description("extracted assay from the user query i.e. flow cytometry, sequencing, etc.")
    attribute string[]? | string? @description("extracted attribute from the user query i.e. genotype, treatment, species, etc.")
    terms string[]? | string? @description("extracted terms from the user query associated with a specific attribute i.e. 'rituximab' for treatment ")
}