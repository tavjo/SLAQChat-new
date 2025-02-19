function RetrieveSchema(user_query: string, db_schema: Schema) -> SchemaMapper {
    client MyClient
    prompt #"
        You are a schema extraction agent. Below is the current database schema (in JSON format) and a user query. 
        Ignore irrelevant tables. Focus on identifying the exact table and column that contain sample-specific genotype information. 
        In our database, the table 'seek_production.samples' contains a JSON column 'json_metadata' that holds sample-specific data. 
        From this column, extract the keys that are used for identifying a sample according to key words from the user query. 
        Ensure that you retrieve all the keys that are relevant to the user query.
        It is better to retrieve more keys than is necessary than to retrieve too few keys.

        {{ db_schema}}
        {{ user_query}}
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
