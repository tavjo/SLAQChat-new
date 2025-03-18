class QueryParser {
    parsed_query ParsedQuery @description("Parsed user query")
    // tasks string[] @description("List of tasks to be performed")
    explanation string @description("Explanation of your reasoning (how you arrived at the parsed query)")
    justification string @description("The justification for your reasoning (why you chose the parsed query)")
}

// client<llm> ParseQueryClient {
//     provider "openai"
//     options {
//         api_key env.OPENAI_API_KEY
//         model "gpt-4o"
//         temperature 0
//     }
// }
function ParseQuery(context: Payload) -> QueryParser {
    client Reasoner
    prompt  #"
    You are a query parser that breaks down complex user queries {{ context.user_query }} into atomic parts.
    Your goal is to create a clear and structured version of the user query.

    Example:
    User: "Please list all samples with genotype ''RaDR+/+; GPT+/+; Aag -/-'?"
    Parsed query would be:
    {
        "attribute" "genotype",
        "terms" "RaDR+/+; GPT+/+; Aag -/-"
    }

    If you are unsure about the tasks, you can ask the user for clarification by returning a question as the parsed_query and justification as "I am unsure about the tasks. Please clarify your query."

    {{ context }}
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