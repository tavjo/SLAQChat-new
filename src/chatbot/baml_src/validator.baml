// Defining a data model.
class Validator {
    Valid bool
    Clarifying_Question string
    Metadata string
    Next_worker string
}

// Create a function to validate the response from the responder.
function ValidateResponse(response: string) -> Validator {
  client "openai/gpt-4o" // Set OPENAI_API_KEY to use this client.
  prompt #"
    Validate the response from the responder. The next worker should always be the 'responder' unless otherwise specified in the response. Return the metadata in the response as a string.
    {{ response }}

    {{ ctx.output_format }}
  "#
}

// Test the function with a sample response. Open the VSCode playground to run this.
test myresponse {
    functions [ValidateResponse]
    args {
        response #"
            [HumanMessage(content='Can you tell me a little about this sample: NHP-220630FLY-15?', additional_kwargs={}, response_metadata={}, id='fd2f06da-48fd-4049-91c2-89a3ca43d387'), HumanMessage(content='Summary: The sample "NHP-220630FLY-15" is a male Macaca fascicularis, originating from China and housed at the Flynn Lab. The sample is part of the "IgG" cohort and is involved in the "CD8 Depletion" study, funded by NIH R56AI139053, which investigates the role of CD8 T cells in controlling tuberculosis. The sample has a total Colony Forming Unit (CFU) count of 2,392,635, with specific counts in the lung and lymph nodes. The total pathology score is 41, with lung and lymph node scores of 15 and 22, respectively. The study design includes specific depletion and necropsy dates, and the protocol used is documented in "P.FLY-220823-V1_P---NHP_housing.docx".\n\nMetadata: \n```json\n{\n    "UID": "NHP-220630FLY-15",\n    "Name": "29918",\n    "DateOfBirth": "2013-08-08 00:00:00",\n    "Sex": "M",\n    "Species": "Macaca fascicularis",\n    "Origin": "China",\n    "Facility": "Flynn Lab",\n    "Notes": "JF/PL19-40A",\n    "Scientist": "JoAnne Flynn",\n    "Publish_uri": "https://fairdomhub.org/samples/19993",\n    "Cohort": "IgG",\n    "Study": "CD8 Depletion",\n    "Funder": "NIH R56AI139053 Contribution of CD8 T cells in controlling tuberculosis (MPI Flynn/Lin)",\n    "TotalCFU": "2392635",\n    "LungCFU": "1169675",\n    "LymphNodeCFU": "1222960",\n    "TotalPathologyScore": "41",\n    "LungPathologyScore": "15",\n    "LymphNodePathologyScore": "22",\n    "CFUUnits": "Colony Forming Unit Counts",\n    "StudyDesign": "Depletion: 2019-03-06 00:00:00; LibP: 2019-03-21 00:00:00; Nx: 2019-05-06 00:00:00",\n    "Link_StudyDesign": "http://fairdata.mit.edu:8080/seek/datafile/uid=D.FILE-240216FLY-2_CD8-Depletion.jpg/",\n    "Protocol": "P.FLY-220823-V1_P---NHP_housing.docx"\n}\n```', additional_kwargs={}, response_metadata={}, name='basic_sample_info_retriever', id='1a7ca988-96df-4114-9722-0c402f7d18d5')]
        "#
    }
}