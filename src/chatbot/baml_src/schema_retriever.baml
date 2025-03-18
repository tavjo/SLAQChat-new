function RetrieveSchema(user_query: string, db_schema: DBSchema, parsed_query: ParsedQuery) -> SchemaMapper {
    client Reasoner
    prompt #"
        Map the user query: \n{{ user_query }} \nto the database schema: \n{{db_schema}} using the parsed query {{parsed_query}} as guidance.
        The relevant database table is `seek_production.samples` which contains a JSON column 'json_metadata' with sample-specific metadata.
        Extract only the keys that are actually present in the schema and are also relevant to the user query. 
        Do not invent any keys; if a key is not in the schema, omit it.
        For example, if the user asks for 'samples of genotype X', return the closest matching keys from the schema such as 'UID' and 'Genotype'. 
        If the user query is not related to the database, return 'No relevant information found in the database.' 
        \nImportant: Only return the relevant keys from the json_metadata column of the schema, the database schema as a json object, and your justification. Do not return any other information such as speculated keys or proposed queries.
        {{ctx.output_format}}
    "#
}

test retrieveSchema {
    functions [RetrieveSchema]
    args {
        user_query #"Retrieve UIDs of all samples of this genotype: 'RaDR+/+; GPT+/+; Aag -/-'"#
        db_schema {
                tables [
                {
                    name "seek_production.projects_samples"
                    columns [
                        {
                            name "project_id"
                            type "INTEGER"
                            nullable true
                            default null
                        },
                        {
                            name "sample_id"
                            type "INTEGER"
                            nullable true
                            default null
                        }]},
                {
                    name "seek_production.samples"
                    columns [
                        {
                            name "id"
                            type "INTEGER"
                            nullable false
                            default null
                        },
                        {
                            name "title"
                            type "VARCHAR(255)"
                            nullable true
                            default null
                        },
                        {
                            name "sample_type_id"
                            type "INTEGER"
                            nullable true
                            default null
                        },
            {
            name "json_metadata"
            type "TEXT"
            nullable true
            default null
            json_keys [
                "Treatment2Dose",
                "RepositoryID",
                "StorageSite",
                "Type",
                "AntibodyParent",
                "Reference",
                "TreatmentTimeUnits",
                "Protocol_Treatment",
                "UID",
                "Genotype",
                "ReagentManufacturer",
                "QC",
                "Concentration",
                "TreatmentDoseTime",
                "TreatmentRoute",
                "TotalProteinUnits",
                "SourceFacility",
                "Species",
                "Notes",
                "CellLineage",
                "Parent",
                "PassageNum",
                "Treatment2",
                "ValidationMethod",
                "FMO",
                "Scientist",
                "Protocol_Stimulation",
                "Timepoint",
                "Repository",
                "ValidationQuality",
                "Treatment1Dose",
                "Publish_uri",
                "CellCount",
                "BioSampleAccession",
                "Protocol",
                "QC_notes",
                "Media",
                "Treatment1Reference",
                "Treatment1DoseUnits",
                "Checksum_PrimaryType",
                "StorageTemperature",
                "TotalProtein",
                "ReagentBrand",
                "Instrument",
                "Treatment2Reference",
                "Phenotype",
                "Stain",
                "Fixation",
                "Fixative",
                "ReagenCatalogNum",
                "Name",
                "FlowAmount",
                "Treatment2DoseUnits",
                "TreatmentType",
                "SEEKSubmissionDate",
                "StorageLocation",
                "Vendor",
                "ConcentrationUnits",
                "Software",
                "Stimulation",
                "SampleCreationDate",
                "Link_PrimaryData",
                "Checksum_PrimaryData",
                "File_PrimaryData",
                "Reagent",
                "CellLine",
                "InstrumentUser",
                "Treatment1",
                "StorageTemperatureUnits",
                "Catalog#",
                "BiosafetyLevel",
                "FlowAmountUnits",
                "Source",
                "CompensationFCSParent",
                "Path_PrimaryData",
                "StorageType"
                        ]
                    },
            {
                name "uuid"
                type "VARCHAR(255)"
                nullable true
                            default null
                        },
            {
                name "contributor_id"
                type "INTEGER"
                nullable true
                default null
            },
            {
                name "policy_id"
                type "INTEGER"
                nullable true
                default null
            },
            {
                name "created_at"
                type "DATETIME"
                nullable false
                default null
            },
            {
                name "updated_at"
                type "DATETIME"
                nullable false
                default null
            },
            {
                name "first_letter"
                type "VARCHAR(1)"
                nullable true
                default null
            },
            {
                name "other_creators"
                type "TEXT"
                nullable true
                default null
            },
            {
                name "originating_data_file_id"
                type "INTEGER"
                nullable true
                default null
            },
            {
                name "deleted_contributor"
                type "VARCHAR(255)"
                nullable true
                default null
                        }
                    ]
                }
            ]
        }
    }
}
