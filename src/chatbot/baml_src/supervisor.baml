
// Define Supervisor class
// Create a function to validate the response from the responder.
client<llm> SupervisorClient {
  provider "openai"
  options {
    api_key env.OPENAI_API_KEY
    model "gpt-4o"
    temperature 0
  }
  retry_policy MaxRetries
}

function Supervise(Messages: Payload, workers: Agent[]) -> Supervisor {
    client Reasoner
  prompt #"
    {{ GetSystemPrompt() }}
    {{ GetNExtSEEKIntro() }}

    Your role is to route tasks to specialized workers based on user queries.

    If none of the workers have the capability to answer the user query, then you should route the user query to the "responder" worker.

    **Important:** Never choose the same worker twice in a row. 
    
    If no response is provided by the chosen worker (determined  by the names in {{ Messages.aggregatedMessages }}), then route to the "responder" worker.

    Key responsibilities:
    1. Analyze the user query and available worker capabilities
    2. Choose the most appropriate worker to handle the current task
    3. Track conversation context in aggregatedMessages
    4. Route to "responder" when ready to deliver final answer
    5. If no workers are available, always route to "FINISH"
    6. NEVER make up an answer. If the answer is not already in the resources or the conversation history, clearly state that you do not know the answer or that you do not have the tools necessary to answer the question.

    User Query:
    {{ Messages.user_query }}

    {{ _.role("system") }}
    Current conversation state and available workers:

    {{ _.role("user") }}
    {{ PrintMessages(Messages.aggregatedMessages) }}

    Available Workers:
    {% for worker in workers %}
    --- Worker: {{ worker.agent }}
    --- Role: {{ worker.role }}
    --- Toolbox: {{ worker.toolbox }}
    {% endfor %}
    {{ ctx.output_format }}
  "#
}
test mysupervisor {
    functions [Supervise]
    args {
        Messages {
                system_message #"You are a helpful assistant that is tasked with answering user questions about a data management platform called NExtSEEK."#
                user_query #"Can you tell me a little about the sample NHP-220630FLY-15?"#
                aggredatedMessages [#"Can you tell me a little about the sample NHP-220630FLY-15?"#]
            }
        workers [
            {
            agent "basic_sample_info_retriever"
            role "Retrieve basic sample info for the sample"
            messages {
                system_message null
                user_query null
                aggredatedMessages null
            }
            resource {
            }
            toolbox ["get_sample_name", "retrieve_sample_info"]
            tools_description {
            "get_sample_name" #"Get the name of the sample.\nArgs:\nsample_metadata (list): A list of dictionaries containing sample metadata.\nReturns: str: The name of the sample."#
            "retrieve_sample_info" #"Retrieve the sample information for a given sample UID.\nArgs:\nuid (str): The UID of the sample.\nReturns:\nList[dict] | None: A list containing the metadata dictionary for the sample or None if an error occurred."#
        }
            },
            {
                agent "responder"
                role "Validate and respond to the user's query"
                messages {
                    system_message null
                    user_query null
                    aggredatedMessages null
                }
                resource {}
            }
        ]
    }
}