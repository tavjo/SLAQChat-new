
function Navigate(agent: Agent) -> Navigator {
    client MyClient
    prompt #"
        Determine the next tool to use to answer the user's query.
        Return the **exact** name of the agent provided in {{agent}} for the next_agent. 
        Choose a tool from the toolbox and return the name of the tool as the next_tool, not the agent name or the description of the tool.
        Return exactly the argument to pass to the tool as the tool_arg based on the user_query and the summedMessages.
        Return the justification for your choice of tool and the next_agent.
        {{agent}}
        {{ ctx.output_format }}
    "#
}

test navigator {
    functions [Navigate]
    args {
        agent {
            agent "basic_sample_info_retriever"
            messages {
                system_message #"You are a helpful assistant that is tasked with answering user questions about a data management platform called NExtSEEK."#
                user_query #"Can you tell me a little about the sample NHP-220630FLY-15?"#
                aggredatedMessages [#"Can you tell me a little about the sample NHP-220630FLY-15?"#]
            }
            resource {
            }
            toolbox ["get_sample_name", "retrieve_sample_info"]
            tools_description {
            "get_sample_name" #"Get the name of the sample.\nArgs:\nsample_metadata (list): A list of dictionaries containing sample metadata.\nReturns: str: The name of the sample."#
            "retrieve_sample_info" #"Retrieve the sample information for a given sample UID.\nArgs:\nuid (str): The UID of the sample.\nReturns:\nList[dict] | None: A list containing the metadata dictionary for the sample or None if an error occurred."#
        }
    }
    }
}
