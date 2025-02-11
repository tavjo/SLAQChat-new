
// Define Supervisor class


function Supervise(Messages: Messages, workers: Agent[]) -> Supervisor {
    client MyClient
    prompt #"
        You are a supervisor that decides which worker to call next based on the user's query.
        Decide which worker from the list of workers to call next based on the user's query and/or the messages from the previous worker and the worker's description.
        **Only call the necessary workers to answer the user's query.**
        Return the next worker, the aggregated messages, and the user's query.
        If no worker has been called yet, return the user's query for aggregatedMessages.
        When receive a response from a worker, use the result to answer the user's query. 
        Maintain any special formatting in your response such as urls/links, json format etc. while briefly summarizing the information. 
        If you have enough information to fully answer the user's query, return the next worker as "responder".  
        {{ Messages }}
        {{ workers }}
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