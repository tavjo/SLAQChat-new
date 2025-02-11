
// Define Supervisor class


function Supervise(Messages: Messages, workers: Agent[]) -> Supervisor {
    client MyClient
  prompt #"
    You are a workflow supervisor that routes tasks to specialized workers based on user queries.

    Key responsibilities:
    1. Analyze the user query and available worker capabilities
    2. Choose the most appropriate worker to handle the current task
    3. Track conversation context in aggregatedMessages
    4. Route to "responder" when ready to deliver final answer

    {{ ctx.output_format }}

    {{ _.role("system") }}
    Current conversation state and available workers:

    {{ _.role("user") }}
    Messages: {{ Messages }}
    Workers: {{ workers }}
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