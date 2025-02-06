// Defining a data model.
class Responder {
    Next_worker string @description("The next worker to call")
    aggregatedMessages string @description("Same as inputMessage")
    user_query string @description("The original user query")
    // prev_worker string @description("The previous worker that was used")
}

// Create a function to respond to the user's query.
function Respond(inputMessage: string, workers: map<string, string>, user_query: string, prev_worker: string) -> Responder {
    client MyClient
      prompt #"
        Sequentially use the workers in the order of {{ workers }} to respond to the user's query. 
        If the worker has 'optional' in the name, only use it as needed.
        Never return the same worker name multiple times.
        Return the next worker as the worker's name (i.e. 'validator') as provided in the workers map.
        Once you have a response from the "validator", the next worker must be "FINISH".
        {{inputMessage}}
        {{user_query}}
        {{prev_worker}}
        {{ ctx.output_format }}
  "#
}

// Test the function with a sample input. Open the VSCode playground to run this.
test myresponse {
    functions [Respond]
    args {
        inputMessage #"
            The protocol for the sample NHP-220630FLY-15 can be accessed [here](https://nextseek.mit.edu/seek/sop/uid=P.FLY-220823-V1_P---NHP_housing.docx/).
        "#
        workers #"
            "data_summarizer" "1.(optional) Summarize the data if response is longer than 100 words"
            "response_formatter" "2.(optional)Format the response if data_summarizer is used"
            "validator" "3.Validate the response"
            "FINISH" "4.Finish the conversation"
        "#
        user_query #"What is the protocol for the sample NHP-220630FLY-15?"#
    }
}
