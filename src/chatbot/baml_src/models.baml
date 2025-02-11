class DataSummarizer {
    Next_worker string @description("The next worker to call : 'responder'")
    summary string @description("The summary of the input message")
    messages Messages @description("The messages in the conversation")
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
    Next_worker string @description("The next worker to call : responder")
    formattedResponse string @description("The formatted response to the user")
    name string @description("The name of the current worker : response_formatter")
    messages Messages @description("The messages in the conversation")
    justification string @description("The justification for your response")
}

class Supervisor {
    Next_worker Agent @description("The next worker to call")
    justification string @description("The justification for choosing the next worker")
}

class ResourceBox {
    sample_metadata Metadata[]? @description("The metadata of the sample")
    protocol_link string? @description("The link to download the protocol associated with a sample")
    link string? @description("The link to the sample: https://nextseek.mit.edu/seek/sampletree/uid=<sample_uid>")
}

class Metadata {
    UID string?
    Name string?
    ID string?
    DateOfBirth string?
    Sex string?
    Species string?
    Origin string?
    Facility string?
    Notes string?
    Contact string?
    Scientist string?
    Publish_uri string?
    CoScientist string?
    Treatment1 string?
    Treatment1Type string?
    Treatment1Route string?
    Treatment1Date string?
    Treatment1Dose string?
    Treatment1DoseUnits string?
    Treatment2 string?
    Treatment2Type string?
    Treatment2Route string?
    Treatment2Date string?
    Treatment2Dose string?
    Treatment2DoseUnits string?
    NecropsyDate string?
    Cohort string?
    Supplier string?
    Treatment3 string?
    Treatment3Type string?
    Protocol string?
    Study string?
    Funder string?
    TotalCFU string?
    LungCFU string?
    LymphNodeCFU string?
    TotalPathologyScore string?
    LungPathologyScore string?
    LymphNodePathologyScore string?
    CFUUnits string?
    AlternativeID string?
    StudyDesign string?
    Link_StudyDesign string?
    NewGranulomaCount string?
    nhp_id string?
    LINK string?
    START_DATE string?
    STOP_DATE string?
    TYPE string?
    PATIENT_ID string?
    EVENT_TYPE string?
    STUDY_DESIGN_NOTES string?
    DOSE string?
    TREATMENT_PARENT string?
    ORGAN_DETAIL string?
    ORGAN string?
    TREATMENT string?
    CFU string?
    NAME string?
    DOSE_UNITS string?
    SAMPLE_ID string?
    ROUTE string?
    PARENT string?
    Treatment3Route string?
    Treatment3Date string?
    Treatment3Dose string?
    Treatment3DoseUnits string?
}

class Messages {
    system_message string @description("The system message")
    user_query string @description("The user message")
    aggredatedMessages string[]? @description("The aggregated messages in the conversation")
    resource ResourceBox? @description("The resources available to the agent")
}

class Agent {
    agent string @description("The name of the agent")
    role string @description("The role of the agent")
    messages Messages @description("The messages in the conversation")
    toolbox string[]? @description("The toolbox of the agent")
    tools_description map<string, string>? @description("The description of the tools in the toolbox")
}

class Validator {
    name string @description("The name of the current agent : validator")
    Valid bool @description("Whether the response is valid")
    Clarifying_Question string? @description("A clarifying question to the user if Valid is false")
    justification string @description("The justification for your response")
    Next_worker string @description("The next worker to call : responder")
    response Messages @description("same as inputMessage")
}