
// Define Supervisor class
class Supervisor {
    Next_worker string @description("The next worker to call")
    aggregatedMessages string @description("The aggregated responses from all workers used")
    user_query string @description("The user's query")
}

function Supervise(Messages: string, workers: map<string, string>) -> Supervisor {
    client MyClient
    prompt #"
        You are a supervisor that decides which worker to call next based on the user's query.
        Decide which worker from the list of workers to call next based on the user's query and/or the messages from the previous worker and the worker's description.
        **Only call the necessary workers to answer the user's query.**
        Return the next worker, the aggregated messages, and the user's query.
        If no worker has been called yet, return the user's query for aggregatedMessages.
        Once you have enough information to answer the user's query, return the next worker as "responder".
        {{ Messages }}
        {{ workers }}
        {{ ctx.output_format }}

    "#
}
test mysupervisor {
    functions [Supervise]
    args {
        Messages #"
            What is the protocol for the sample NHP-220630FLY-15?
        "#
        workers {
            "descendant_metadata_retriever" "Retrieve descendant metadata for the sample"
            "link_retriever" "Retrieve link for the sample and/or the associatedprotocol"
            "basic_sample_info_retriever" "Retrieve basic sample info for the sample"
            "responder" "Validate and respond to the user's query"
        }
    }
}