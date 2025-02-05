// Defining a data model.
class Responder {
    Next_worker string
    Aggregated_Messages string
    formattedResponse string
    name string
}

// Create a function to respond to the user's query.
function Respond(inputMessage: string) -> Responder {
    client "openai/gpt-4o" // Set OPENAI_API_KEY to use this client.
      prompt #"
    Use responses from previous workers to respond to the user's query. You have 3 options for the next worker: "validator", "data_summarizer", or "FINISH".
    Check name of previous worker in {{inputMessage}}. If name is "validator", decide whether to use "data_summarizer" or "FINISH" for the next worker depending on the length of {{inputMessage}}. 
    Return the next worker and the aggregated messages (same as inputMessage) as a string but leave the formatted response blank unless you are ready to respond to the user. 
    Once you are ready to respond to the user, return the formatted response as a string that is a summary of {{inputMessage}}. 
    If the validator returns a clarifying question, the formatted response should only be the clarifying question. 
    When you are ready to respond to the user, return the next worker as "FINISH" along with the formatted response. 
    The name should be the name of the current worker: "responder".

    {{ ctx.output_format }}
  "#
}

// Test the function with a sample input. Open the VSCode playground to run this.
test myresponse {
    functions [Respond]
    args {
        inputMessage #"
            {
            "Valid": true
            "Clarifying_Question": "", 
            "originalMessage": "Summary: The sample "NHP-220630FLY-15" is a male Macaca fascicularis, originating from China and housed at the Flynn Lab. The sample is part of the "IgG" cohort and is involved in the "CD8 Depletion" study, funded by NIH R56AI139053, which investigates the role of CD8 T cells in controlling tuberculosis. The sample has a total Colony Forming Unit (CFU) count of 2,392,635, with specific counts in the lung and lymph nodes. The total pathology score is 41, with lung and lymph node scores of 15 and 22, respectively. The study design includes specific depletion and necropsy dates, and the protocol used is documented in "P.FLY-220823-V1_P---NHP_housing.docx".

            Metadata: 
            ```json
            {
                "UID": "NHP-220630FLY-15",
                "Name": "29918",
                "DateOfBirth": "2013-08-08 00:00:00",
                "Sex": "M",
                "Species": "Macaca fascicularis",
                "Origin": "China",
                "Facility": "Flynn Lab",
                "Notes": "JF/PL19-40A",
                "Scientist": "JoAnne Flynn",
                "Publish_uri": "https://fairdomhub.org/samples/19993",
                "Cohort": "IgG",
                "Study": "CD8 Depletion",
                "Funder": "NIH R56AI139053 Contribution of CD8 T cells in controlling tuberculosis (MPI Flynn/Lin)",
                "TotalCFU": "2392635",
                "LungCFU": "1169675",
                "LymphNodeCFU": "1222960",
                "TotalPathologyScore": "41",
                "LungPathologyScore": "15",
                "LymphNodePathologyScore": "22",
                "CFUUnits": "Colony Forming Unit Counts",
                "StudyDesign": "Depletion: 2019-03-06 00:00:00; LibP: 2019-03-21 00:00:00; Nx: 2019-05-06 00:00:00",
                "Link_StudyDesign": "http://fairdata.mit.edu:8080/seek/datafile/uid=D.FILE-240216FLY-2_CD8-Depletion.jpg/",
                "Protocol": "P.FLY-220823-V1_P---NHP_housing.docx"
            }
            ```", 
            "Next_worker": "responder", 
            "name": "validator", 
            }
        "#
    }
}
