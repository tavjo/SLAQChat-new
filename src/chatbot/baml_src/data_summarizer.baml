class DataSummarizer {
    Next_worker string @description("The next worker to call : 'responder'")
    summary string @description("The summary of the input message")
    user_query string @description("The user's query")
}

function SummarizeData(inputMessage: string, user_query: string) -> DataSummarizer {
    client MyClient
    prompt #"
    Summarize the input message in a concise manner. Ensure the summary remains relevant to the user's query. If the input message is already concise, return it as the summary.
    {{inputMessage}}
    {{user_query}}
    {{ctx.output_format}}
    "#
}

test summary {
    functions [SummarizeData]
    args {
        inputMessage #"
            The protocol for the sample NHP-220630FLY-2 can be accessed [here](https://nextseek.mit.edu/seek/sop/uid=P.FLY-220823-V1_P---NHP_housing.docx/).
        "#
        user_query #"
            What is the protocol for the sample NHP-220630FLY-2?
        "#
    }
}
