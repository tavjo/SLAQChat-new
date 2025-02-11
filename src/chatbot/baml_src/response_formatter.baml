function FormatResponse(user_query: string, messages: Messages, resources: ResourceBox) -> ResponseFormatter {

    client MyClient
        prompt #"

        Use the resources {{resources}} and the messages {{messages}} in the conversation as ground truth to answer the user's query {{user_query}}. 
        Never make up information or make assumptions. Only use the information provided in the resources and the messages.
        Maintain any special formatting in your response such as urls/links, json format etc. as provided in the resources while briefly summarizing the information in the messages.
        Your response should look like this:
        - Summary of messages from the conversation that answers the user's query
        - Any relevant resources from the resources box exactly as is.
        - If the user's query is not answered in the messages, say so.

        {{ctx.output_format}}
        "#
}

test myresponse {

    functions [FormatResponse]
    args {
        user_query #"Can you tell me more about the sample with UID PAV-220630FLY-1031?"#
        messages {
            system_message #"You are a helpful assistant that is a part of a network of workers tasked with answering user questions about a data management platform called NExtSEEK."#
            user_query #"Can you tell me more about the sample with UID PAV-220630FLY-1031?"#
            aggredatedMessages [#"Can you tell me more about the sample with UID PAV-220630FLY-1031?"#, #"Summary: The sample with UID 'PAV-220630FLY-1031' is named '29518-190327' and is associated with the scientist JoAnne Flynn. It is categorized as a 'Scan' type sample and is linked to the protocol 'P.FLY-231011-V1_Patient-Visit-CD8.docx'. The sample was created on March 27, 2019, and is part of the Flynn Lab. Additional notes mention 'P0099'. The sample is a child of 'NHP-220630FLY-2'. More details can be found at the provided URI."#]
        }
        resources {
            sample_metadata [
            {
                "UID" "PAV-220630FLY-1031"
                "Name" "29518-190327"
                "Scientist" "JoAnne Flynn"
                "RecordDate" ""
                "Protocol" "P.FLY-231011-V1_Patient-Visit-CD8.docx"
                "Type" "Scan"
                "Procedure" ""
                "CollectionTime" ""
                "Parent" "NHP-220630FLY-2"
                "VisitFacility" "Flynn Lab"
                "VisitLocation" ""
                "Notes" "P0099"
                "Publish_uri" "https://fairdomhub.org/samples/23142"
            }]
        }
    }
}

