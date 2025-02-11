function FormatResponse(messages: Messages) -> ResponseFormatter {

    client MyClient
        prompt #"

    Format a response using only the provided messages and resources. 

    Guidelines:
    - Only use information from provided sources
    - Preserve any special formatting (URLs, JSON, etc.)
    - Indicate if information is insufficient to answer
    - Structure the response clearly with bullet points when appropriate

    {{ messages }}
    {{ctx.output_format}}
        "#
}

test BasicFormatting {
  functions [FormatResponse]
  args {
    messages {
      system_message "You are a helpful lab assistant"
      user_query "What protocol should I use for sample MIT-123?"
      aggregatedMessages ["What protocol should I use for sample MIT-123?"]
    }
  }
}

test myresponse {

    functions [FormatResponse]
    args {
        messages {
            system_message #"You are a helpful assistant that is a part of a network of workers tasked with answering user questions about a data management platform called NExtSEEK."#
            user_query #"Can you tell me more about the sample with UID PAV-220630FLY-1031?"#
            aggredatedMessages [#"Can you tell me more about the sample with UID PAV-220630FLY-1031?"#, #"Summary: The sample with UID 'PAV-220630FLY-1031' is named '29518-190327' and is associated with the scientist JoAnne Flynn. It is categorized as a 'Scan' type sample and is linked to the protocol 'P.FLY-231011-V1_Patient-Visit-CD8.docx'. The sample was created on March 27, 2019, and is part of the Flynn Lab. Additional notes mention 'P0099'. The sample is a child of 'NHP-220630FLY-2'. More details can be found at the provided URI."#]
            resource {
                sample_metadata [
                    {
                        UID "PAV-220630FLY-1031"
                        Name "29518-190327"
                        Scientist "JoAnne Flynn"
                        RecordDate ""
                        Protocol "P.FLY-231011-V1_Patient-Visit-CD8.docx"
                        Type "Scan"
                        Parent "NHP-220630FLY-2"
                        VisitFacility "Flynn Lab"
                        VisitLocation ""
                        Notes "P0099"
                        Publish_uri "https://fairdomhub.org/samples/23142"
                    }],
                protocolUrl "https://nextseek.mit.edu/seek/sop/uid=P.FLY-231011-V1_Patient-Visit-CD8.docx"
                sampleUrl "https://nextseek.mit.edu/seek/sampletree/uid=PAV-220630FLY-1031"
            }
        }
    }
}

