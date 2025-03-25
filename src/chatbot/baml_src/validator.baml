// Create a function to validate the response from the responder.
// client<llm> ValidatorClient {
//   provider "openai"
//   retry_policy MaxRetries
//   options {
//     api_key env.OPENAI_API_KEY
//     model "gpt-4o"
//     temperature 0.5
//   }
// }

function ValidateResponse(inputMessage: Payload) -> Validator {
  client Reasoner
  prompt #"
    {{ GetSystemPrompt() }}
    {{ GetNExtSEEKIntro() }}
  
    Your role is to analyze the conversation and validate if the response adequately addresses the user's query.

    Validation Checklist:
    1. Check if all parts of the user's query are addressed
    2. Verify any resources or links mentioned are present in the ResourceBox
    3. Ensure no information is fabricated
    4. Confirm technical accuracy and format consistency
    5. Important: Always address your clarifying questions to the **user**.
    6. Don't assume an information is wrong, only address gaps in the information provided based on the user's query

    If invalid, you should either:
      1. Provide a specific clarifying question addressing the gap, OR
      2. Summarize the error for the user in a polite and friendly manner if the response is invalid because an error occurred at any point in the previous workers.

    User Query:
    {{ inputMessage.user_query }}

    Conversation History:
    {{ PrintMessages(inputMessage.aggregatedMessages) }}

    Resources:
    {{ inputMessage.resource }}

    {{ ctx.output_format }}
  "#
}

// Test the function with a sample response. Open the VSCode playground to run this.
test validateResponse {
    functions [ValidateResponse]
    args {
        inputMessage {
            system_message #"You are a helpful assistant that is a part of a network of workers tasked with answering user questions about a data management platform called NExtSEEK."#
            user_query #"Can you tell me more about the sample with UID PAV-220630FLY-1031?"#
            aggredatedMessages [#"Can you tell me more about the sample with UID PAV-220630FLY-1031?"#, #"Summary: The sample with UID 'PAV-220630FLY-1031' is named '29518-190327' and is associated with the scientist JoAnne Flynn. It is categorized as a 'Scan' type sample and is linked to the protocol 'P.FLY-231011-V1_Patient-Visit-CD8.docx'. The sample was created on March 27, 2019, and is part of the Flynn Lab. Additional notes mention 'P0099'. The sample is a child of 'NHP-220630FLY-2'. More details can be found at the provided URI."#, #"Here are the details for the sample with UID PAV-220630FLY-1031:\n\n- **Name**: 29518-190327\n- **Notes**: P0099\n- **Scientist**: JoAnne Flynn\n- **Protocol**: [P.FLY-231011-V1_Patient-Visit-CD8.docx](https://nextseek.mit.edu/seek/sop/uid=P.FLY-231011-V1_Patient-Visit-CD8.docx)\n- **Publish URI**: [Sample Link](https://fairdomhub.org/samples/23142)\n- **Sample URL**: [Sample Details](https://nextseek.mit.edu/seek/sampletree/uid=PAV-220630FLY-1031)"#]
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
        }
    }
}