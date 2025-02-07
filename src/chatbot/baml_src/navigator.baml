class Navigator {
    agent string @description("The name of the agent (same as input)")
    user_query string @description("The user's query verbatim")
    next_tool string @description("The next tool to use")
    tool_arg string @description("The argument to pass to the tool")
    summedMessages string[]|null @description("The messages in the conversation")
}

function Navigate(agent: string, toolbox: string[], tools_description: map<string, string>, user_query: string, summedMessages: string[]|null) -> Navigator {
    client MyClient
    prompt #"
        Determine the next tool to use to answer the user's query.
        Return the **exact** name of the agent provided in {{agent}} for the next_agent. 
        Choose a tool from the toolbox and return the name of the tool as the next_tool, not the agent name or the description of the tool.
        Return exactly the argument to pass to the tool as the tool_arg based on the user_query and the summedMessages.

        {{agent}}
        {{toolbox}}
        {{tools_description}}
        {{user_query}}
        {{summedMessages}}
        {{ ctx.output_format }}
    "#
}

test navigator {
    functions [Navigate]
    args {
        agent "link_retriever"
        toolbox ["add_links", "fetch_protocol"]
        tools_description {
            "add_links" #"Constructs a link to the sample's page on the NExtSEEK website or constructs a link to download a protocol associated with a sample.\nArgs:\nsample_uid (str): Sample UID that will be used to construct the link.\nReturns: str: Link to the sample's page on the NExtSEEK website."#
            "fetch_protocol" #"Fetch the protocol for a given sample UID if it exists.\nArgs:\nuid (str): The UID of the sample.\nReturns: str | None: The protocol link for the sample or None if no protocol is found."#
        }
        user_query #"What is the protocol for the sample NHP-220630FLY-15?"#
        summedMessages null
    }
}
