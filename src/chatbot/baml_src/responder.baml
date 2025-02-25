// Create a function to respond to the user's query.
function Respond(inputMessage: Payload, workers: Agent[]) -> Responder {
    client MyClient
      prompt  #"
    You are a workflow coordinator selecting the next appropriate worker to handle this conversation.

    Worker Selection Rules:
    1. Workers must be used in this sequence: {{ workers }}
    2. Workers must be used in the order of the list 
    3. Workers with 'optional' in name should only be used when necessary
    4. Never repeat a worker
    5. Choose based on the current conversation state and needs
    6. If an error occurred in a previous worker, summarize the error and return the next worker.

    Selection Process:
    - Analyze the current conversation stage
    - Check if optional workers are needed
    - Verify if validation is complete
    - Provide clear justification for your choice

    {{ ctx.output_format }}

    {{ _.role("system") }}
    Available Workers: {{ workers }}
    System Context: {{ inputMessage.system_message }}

    {{ _.role("user") }}
    Current Query: {{ inputMessage.user_query }}

    {% if inputMessage.aggregatedMessages %}
    Conversation History:
    {% for message in inputMessage.aggregatedMessages %}
    - {{ message }}
    {% endfor %}
    {% endif %}

    {% if inputMessage.resource %}
    Active Resources:
    {{ inputMessage.resource }}
    {% endif %}
  "#
}

// Test the function with a sample input. Open the VSCode playground to run this.
test responder {
    functions [Respond]
    args {
        inputMessage {
            system_message #"You are a helpful assistant that is a part of a network of workers tasked with answering user questions about a data management platform called NExtSEEK."#
            user_query #"Can you tell me more about the sample with UID PAV-220630FLY-1031?"#
            aggredatedMessages [#"Can you tell me more about the sample with UID PAV-220630FLY-1031?"#, #"Summary: The sample with UID 'PAV-220630FLY-1031' is named '29518-190327' and is associated with the scientist JoAnne Flynn. It is categorized as a 'Scan' type sample and is linked to the protocol 'P.FLY-231011-V1_Patient-Visit-CD8.docx'. The sample was created on March 27, 2019, and is part of the Flynn Lab. Additional notes mention 'P0099'. The sample is a child of 'NHP-220630FLY-2'. More details can be found at the provided URI."#, #"Here are the details for the sample with UID PAV-220630FLY-1031:\n\n- **Name**: 29518-190327\n- **Notes**: P0099\n- **Scientist**: JoAnne Flynn\n- **Protocol**: [P.FLY-231011-V1_Patient-Visit-CD8.docx](https://nextseek.mit.edu/seek/sop/uid=P.FLY-231011-V1_Patient-Visit-CD8.docx)\n- **Publish URI**: [Sample Link](https://fairdomhub.org/samples/23142)\n- **Sample URL**: [Sample Details](https://nextseek.mit.edu/seek/sampletree/uid=PAV-220630FLY-1031)"#, #"Validation: The response is valid."#]
            resource {
                sample_metadata [
                    {
                        UID "PAV-220630FLY-1031"
                        Name "29518-190327"
                        Scientist "JoAnne Flynn"
                    }
                ],
                protocolUrl "https://nextseek.mit.edu/seek/sop/uid=P.FLY-231011-V1_Patient-Visit-CD8.docx"
                sampleUrl "https://nextseek.mit.edu/seek/sampletree/uid=PAV-220630FLY-1031"
            }
        },
        workers [
            {
                agent "response_formatter"
                role "Aggregate and format information into an answer to the user's query"
                messages {
                    system_message #"You are a helpful assistant that is a part of a network of workers tasked with answering user questions about a data management platform called NExtSEEK."#
                    user_query null
                    aggredatedMessages null
                    resource {
                        sample_metadata null
                        protocolUrl null
                        sampleUrl null
                    }
                }
            },
            {
                agent "validator"
                role "Validate the response from the response formatter"
                messages {
                    system_message #"You are a helpful assistant that is a part of a network of workers tasked with answering user questions about a data management platform called NExtSEEK."#
                    user_query null
                    aggredatedMessages null
                    resource {
                        sample_metadata null
                        protocolUrl null
                        sampleUrl null
                    }
                }
            },
            {
                agent "FINISH"
                role "Finish the conversation"
                messages {
                    system_message #"You are a helpful assistant that is a part of a network of workers tasked with answering user questions about a data management platform called NExtSEEK."#
                    user_query null
                    aggredatedMessages null
                    resource {
                        sample_metadata null
                        protocolUrl null
                        sampleUrl null
                    }
                }
            }
        ]
    }
}