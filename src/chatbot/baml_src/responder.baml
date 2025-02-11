// Create a function to respond to the user's query.
function Respond(inputMessage: Messages, workers: Agent[], prev_worker: string?) -> Responder {
    client MyClient
      prompt #"
        Sequentially use the workers in the order of {{ workers }} to respond to the user's query. 
        If the worker has 'optional' in the name, only use it as needed.
        Never return the same worker name multiple times.
        Once you have a response from the "validator", the next worker must be "FINISH".
        {{inputMessage}}
        {{prev_worker}}
        {{ ctx.output_format }}
  "#
}

// Test the function with a sample input. Open the VSCode playground to run this.
test responder {
    functions [Respond]
    args {
        inputMessage {
            system_message #"You are a helpful assistant that is a part of a network of workers tasked with answering user questions about a data management platform called NExtSEEK."#
            user_query #"Can you tell me more about the sample with UID PAV-220630FLY-1031?"#
            aggredatedMessages [#"Can you tell me more about the sample with UID PAV-220630FLY-1031?"#, #"Summary: The sample with UID 'PAV-220630FLY-1031' is named '29518-190327' and is associated with the scientist JoAnne Flynn. It is categorized as a 'Scan' type sample and is linked to the protocol 'P.FLY-231011-V1_Patient-Visit-CD8.docx'. The sample was created on March 27, 2019, and is part of the Flynn Lab. Additional notes mention 'P0099'. The sample is a child of 'NHP-220630FLY-2'. More details can be found at the provided URI."#]

        },
        workers [
            {
                agent "response_formatter"
                role "Aggregate and format information into an answer to the user's query"
                messages {
                    system_message null
                    user_query null
                    aggredatedMessages null
                }
                resource {}
            },
            {
                agent "validator"
                role "Validate the response from the response formatter"
                messages {
                    system_message null
                    user_query null
                    aggredatedMessages null
                }
                resource {}
            },
            {
                agent "FINISH"
                role "Finish the conversation"
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