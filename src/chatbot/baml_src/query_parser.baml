class QueryParser {
    parsed_query ParsedQuery @description("Parsed user query")
    // tasks string[] @description("List of tasks to be performed")
    explanation string @description("Explanation of your reasoning (how you arrived at the parsed query)")
    justification string @description("The justification for your reasoning (why you chose the parsed query)")
}

// client<llm> ParseQueryClient {
//     provider "openai"
//     retry_policy MaxRetries
//     options {
//         api_key env.OPENAI_API_KEY
//         model "gpt-4o"
//         temperature 0
//     }
// }
function ParseQuery(context: Payload) -> QueryParser {
    client Reasoner
    prompt  #"
      {{ GetSystemPrompt() }}
      {{ GetNExtSEEKIntro() }}
    
    Your task is to breaks down complex user queries {{ context.user_query }} into atomic parts.
    Your goal is to create a clear and structured version of the user query.
    When multiple user queries are detected, you must prioritize the recent query which can be identified by the timestamp. Only use the old queries as additional context to help parse the most recent query.

    Example:
    **Single user query**
    User: "Please list all samples with genotype ''RaDR+/+; GPT+/+; Aag -/-'?"
    Parsed query would be:
    {
        "attribute" "genotype",
        "terms" "RaDR+/+; GPT+/+; Aag -/-"
    }
    **Multiple user query**
    User: "Tell me about the sample 1099 (2025-05-24T19:31:47.378217+00:00); Can you list all the children of that sample? (2025-05-24T19:32:48.193432+00:00)"
    Parsed query would be:
    {
      "UIDs": ["1099"]
    }

    If you are unsure about the tasks, you can ask the user for clarification by returning a question as the explanation and justification as "I am unsure about the tasks. Please clarify your query."

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