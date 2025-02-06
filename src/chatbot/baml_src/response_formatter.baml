class ResponseFormatter {
    Next_worker string @description("The next worker to call : responder")
    formattedResponse string @description("The formatted response to the user")
    name string @description("The name of the current worker : response_formatter")
}

function FormatResponse(user_query: string, inputMessage: string) -> ResponseFormatter {

    client MyClient
        prompt #"

        Format the {{inputMessage}} as a polished response to the user. 
        To polish the inputMessage, remove extra whitespace, name of the worker, and the next worker.
        If original user query is included in the inputMessage string, remove it.
        In the final formatted response, include: 
        1) The summary but remove 'Summary:'.
        2) The metadata in json format but remove fields with empty strings.

        {{inputMessage}}
        {{user_query}}
        {{ctx.output_format}}
        "#
}

test myresponse {

    functions [FormatResponse]
    args {
        inputMessage #"
            Can you tell more more about PAV-220630FLY-1031? Summary: The sample with UID "PAV-220630FLY-1031" is named "29518-190327" and is associated with the scientist JoAnne Flynn. It is categorized as a "Scan" type sample and is linked to the protocol "P.FLY-231011-V1_Patient-Visit-CD8.docx". The sample was created on March 27, 2019, and is part of the Flynn Lab. Additional notes mention "P0099". The sample is a child of "NHP-220630FLY-2". More details can be found at the provided URI.

            Metadata:
            ```json
            {
                "UID": "PAV-220630FLY-1031",
                "Name": "29518-190327",
                "Scientist": "JoAnne Flynn",
                "RecordDate": "",
                "Protocol": "P.FLY-231011-V1_Patient-Visit-CD8.docx",
                "Type": "Scan",
                "Procedure": "",
                "CollectionTime": "",
                "Parent": "NHP-220630FLY-2",
                "VisitFacility": "Flynn Lab",
                "VisitLocation": "",
                "Notes": "P0099",
                "Publish_uri": "https://fairdomhub.org/samples/23142",
                "TestType": "",
                "TestResult": "",
                "TestResultFile": "",
                "Coscientist": "",
                "ProcedureDuration": "",
                "DurationUnits": "",
                "SampleCreationDate": "2019-03-27 00:00:00",
                "BALInstilledVolume": "",
                "BALCollectedVolume": "",
                "VolumeUnits": "",
                "Treatment1": "",
                "Treatment1Type": "",
                "Treatment1Route": "",
                "Treatment1Dose": "",
                "Treatment1DoseUnits": "",
                "Treatment2": "",
                "Treatment2Type": "",
                "Treatment2Route": "",
                "Treatment2Dose": "",
                "Treatment2DoseUnits": "",
                "Treatment3": "",
                "Treatment3Type": "",
                "Treatment3Route": "",
                "Treatment3Dose": "",
                "Treatment3DoseUnits": "",
                "Treatment4": "",
                "Treatment4Type": "",
                "Treatment4Route": "",
                "Treatment4Dose": "",
                "Treatment4DoseUnits": "",
                "Treatment5": "",
                "Treatment5Type": "",
                "Treatment5Route": "",
                "Treatment5Dose": "",
                "Treatment5DoseUnits": "",
                "TestType2": "",
                "TestResult2": "",
                "TestResultFile2": "",
                "TestType3": "",
                "TestResult3": "",
                "TestResultFile3": "",
                "Protocol_Classification": "",
                "Classification": "",
                "ExperimentalTimepoint": "",
                "Treatment1Parent": "",
                "Treatment2Parent": "",
                "Treatment3Parent": "",
                "Treatment4Parent": "",
                "Treatment5Parent": "",
                "NumInjections": ""
            }
            ```.
        "#
    }
}

