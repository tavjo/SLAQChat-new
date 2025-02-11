// Create a function to validate the response from the responder.
function ValidateResponse(inputMessage: Messages) -> Validator {
  client MyClient
  prompt #"
    Validate the relevance of the response to the user's query. 
    Focus on the latest message in the conversation.
    Break down the user query into smaller parts and validate the response against each part.
    The next worker should always be the 'responder' unless otherwise specified in the response. 
    Justify your response.
    {{ inputMessage }}
    {{ ctx.output_format }}
  "#
}

// Test the function with a sample response. Open the VSCode playground to run this.
test myresponse {
    functions [ValidateResponse]
    args {
        inputMessage {
            system_message #"You are a helpful assistant that is a part of a network of workers tasked with answering user questions about a data management platform called NExtSEEK."#
            user_query #"Can you tell me more about the sample with UID PAV-220630FLY-1031?"#
            aggredatedMessages [#"Can you tell me more about the sample with UID PAV-220630FLY-1031?"#, #"Summary: The sample with UID 'PAV-220630FLY-1031' is named '29518-190327' and is associated with the scientist JoAnne Flynn. It is categorized as a 'Scan' type sample and is linked to the protocol 'P.FLY-231011-V1_Patient-Visit-CD8.docx'. The sample was created on March 27, 2019, and is part of the Flynn Lab. Additional notes mention 'P0099'. The sample is a child of 'NHP-220630FLY-2'. More details can be found at the provided URI."#]
        }
    }
}