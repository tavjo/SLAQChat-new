// Defining a data model.
class Validator {
    Valid bool @description("Whether the response is valid")
    Clarifying_Question string @description("A clarifying question to the user if Valid is false")
    originalMessage string @description("The message from the responder")
    Next_worker string @description("The next worker to call : 'responder'")
    name string @description("The name of the current worker : 'validator'")
}

// Create a function to validate the response from the responder.
function ValidateResponse(user_query: string, response: string) -> Validator {
  client MyClient
  prompt #"
    Validate the relevance of the response to the user's query. 
    The next worker should always be the 'responder' unless otherwise specified in the response. Return the original message (response) as a string.
    {{ user_query }}
    {{ response }}

    {{ ctx.output_format }}
  "#
}

// Test the function with a sample response. Open the VSCode playground to run this.
test myresponse {
    functions [ValidateResponse]
    args {
        response #"
            The protocol for the sample NHP-220630FLY-15 can be accessed [here](https://nextseek.mit.edu/seek/sop/uid=P.FLY-220823-V1_P---NHP_housing.docx/).
        "#
        user_query #"What is the protocol for the sample NHP-220630FLY-15?"#
    }
}