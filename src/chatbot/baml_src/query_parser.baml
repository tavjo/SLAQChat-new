class QueryParser {
    parsed_query string @description("Parsed user query")
    tasks string[] @description("List of tasks to be performed")
    justification string @description("Explanation of the reasoning behind the parsed query")
}

client<llm> ParseQueryClient {
    provider "openai"
    options {
        api_key env.OPENAI_API_KEY
        model "gpt-4o"
        temperature 0.7
    }
}
function ParseQuery(user_query: string,context: Payload, tools: map<string, ToolMetadata>) -> QueryParser {
    client ParseQueryClient
    prompt  #"
    You are a query parser that breaks down complex user queries into atomic tasks.
    Your goal is to create a clear sequence of tasks that can be executed to fully answer the query.
    Each task should be self-contained and specific.
    Use conversation history to disambiguate the query. For instance, if the user has mentioned a sample by name in a previous message, then all queries henceforth should be about that sample unless otherwise specified.

    Example:
    User: "What are siblings of sample 123?"
    Tasks would be:
    1. Get parent for sample 123
    2. Get children for parent of sample 123

    If you are unsure about the tasks, you can ask the user for clarification by returning a question as the parsed_query and justification as "I am unsure about the tasks. Please clarify your query."

    {{ _.role("user") }} {{ user_query }}
    {{ context }}
    {{ tools }}
    {{ ctx.output_format }}
  "#
}

test SimpleQueryParse {
  functions [ParseQuery]
  args {
    user_query "What's the weather like in Paris and should I pack an umbrella?"
  }
}

test ComplexQueryParse {
  functions [ParseQuery]
  args {
    user_query "What is the link to the sample page for the parent sample of sample 1099?"
  }
}