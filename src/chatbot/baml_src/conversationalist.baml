class ChatResponse {
    name string @description("The name of the current worker : conversationalist")
    retrieve_info bool @description("Whether to retrieve information from the database")
    response string? @description("The response to the user's query only if retrieve_info is false")
    user_query string @description("The user's query")
    justification string @description("The justification for the response")
}

client<llm> ConversationalistClient {
  provider "openai"
  options {
    api_key env.OPENAI_API_KEY
    model "gpt-4o"
    temperature 0.4
  }
}

function Conversationalist(user_query: string, parsed_query: ParsedQuery) -> ChatResponse {
    client ConversationalistClient
    prompt #"
        You are a helpful assistant tasked with answering user questions about a **data management** platform called NExtSEEK for **scientific research**.
        Examine the user message {{ user_query }} and {{ parsed_query }} to determine if it is a question that requires information to be retrieved from the database.
        If it is, set retrieve_info to true and return the user_query, your justification, and the response should be null.
        If it is not, set retrieve_info to false and return the user_query, your justification, and the response should be a friendly and helpful reply to the user's query.
        Do not make up information. If you do not know the answer, set retrieve_info to 'true' in order to start the process for retrieving information from the database.
        \nImportant: If the user's query is not related to NExtSEEK or data management, set retrieve_info to false and return the user_query, your justification, and the response should be a friendly reply to the user outlining your role. 
        {{ ctx.output_format }}
    "#
}

test converse {
    functions [Conversationalist]
    args {
        user_query #"Hey! What's up?"#
    }
}

test converse2 {
    functions [Conversationalist]
    args {
        user_query #"Hi! Where can I find the protocol for the sample NHP-220630FLY-15?"#
    }
}

test converse3 {
        functions [Conversationalist]
    args {
        user_query #"Hi! Which country has the best food?"#
    }
}




