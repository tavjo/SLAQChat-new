
// client<llm> NavClient {
//   provider "openai"
//   retry_policy MaxRetries
//   options {
//     api_key env.OPENAI_API_KEY
//     model "gpt-4o"
//     temperature 0
//   }
// }

function Navigate(agent: Agent, payload: Payload) -> Navigator {
    client Reasoner
    prompt #"
    You are a navigation system that determines the next appropriate tool to use from an agent's toolbox.

    Instructions:
    1. Analyze the user query {{ payload.user_query }} and conversation context
    2. Select a tool from the agent's toolbox that best addresses the user query
    3. Format tool arguments precisely based on the tool's requirements
    4. Provide clear justification for your tool selection
    5. Do not return a tool if none appear suitable to answer the user query. Instead return an empty string for the tool name and an empty list for the tool arguments.
    6. You must carefully assess the metadadata on the tool selected to ensure that the arguments provided are valid. 
    7. Also, when providing the tool arguments, use the mapped database schema in {{ payload.resource }} to determine the exact database terms to pass in. 
    8. Do not make assumptions about the database schema. Only use the mapped schema in {{ payload.resource }}.

    Constraints:
    - The tool name must exactly match one in the agent's toolbox
    - Tool arguments should be specific and actionable
    - If no suitable tool exists, explain why in the justification
    - Only return the values for the tool arguments 

    - Conversation Context:
    {{ payload }}
    {{ ctx.output_format }}

    {{ _.role("system") }}
    Current agent state and available tools:
    
    Agent Information:
    {{ agent }}

    Agent Toolbox:
    {{ agent.toolbox }}
  "#
}

test navigator {
    functions [Navigate]
    args {
        agent {
            agent "basic_sample_info_retriever"
            role "retrieves basic sample metadata"
            messages {
                system_message #"You are a helpful assistant that is tasked with answering user questions about a data management platform called NExtSEEK."#
                user_query #"What is the weather today?"#
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
