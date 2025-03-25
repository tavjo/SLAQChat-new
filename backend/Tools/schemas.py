# backend/app/models/schemas.py

from pydantic import BaseModel
from typing import Optional, Any, Union


# class Metadata(BaseModel):
#     UID: Optional[Any] = None
#     Name: Optional[Any] = None
#     ID: Optional[Any] = None
#     DateOfBirth: Optional[Any] = None
#     Sex: Optional[Any] = None
#     Species: Optional[Any] = None
#     Origin: Optional[Any] = None
#     Facility: Optional[Any] = None
#     Notes: Optional[Any] = None
#     Contact: Optional[Any] = None
#     Scientist: Optional[Any] = None
#     Publish_uri: Optional[Any] = None
#     CoScientist: Optional[Any] = None
#     Treatment1: Optional[Any] = None
#     Treatment1Type: Optional[Any] = None
#     Treatment1Route: Optional[Any] = None
#     Treatment1Date: Optional[Any] = None
#     Treatment1Dose: Optional[Any] = None
#     Treatment1DoseUnits: Optional[Any] = None
#     Treatment2: Optional[Any] = None
#     Treatment2Type: Optional[Any] = None
#     Treatment2Route: Optional[Any] = None
#     Treatment2Date: Optional[Any] = None
#     Treatment2Dose: Optional[Any] = None
#     Treatment2DoseUnits: Optional[Any] = None
#     NecropsyDate: Optional[Any] = None
#     Cohort: Optional[Any] = None
#     Supplier: Optional[Any] = None
#     Treatment3: Optional[Any] = None
#     Treatment3Type: Optional[Any] = None
#     Protocol: Optional[Any] = None
#     Study: Optional[Any] = None
#     Funder: Optional[Any] = None
#     TotalCFU: Optional[Any] = None
#     LungCFU: Optional[Any] = None
#     LymphNodeCFU: Optional[Any] = None
#     TotalPathologyScore: Optional[Any] = None
#     LungPathologyScore: Optional[Any] = None
#     LymphNodePathologyScore: Optional[Any] = None
#     CFUUnits: Optional[Any] = None
#     AlternativeID: Optional[Any] = None
#     StudyDesign: Optional[Any] = None
#     Link_StudyDesign: Optional[Any] = None
#     NewGranulomaCount: Optional[Any] = None
#     nhp_id: Optional[Any] = None
#     LINK: Optional[Any] = None
#     START_DATE: Optional[Any] = None
#     STOP_DATE: Optional[Any] = None
#     TYPE: Optional[Any] = None
#     PATIENT_ID: Optional[Any] = None
#     EVENT_TYPE: Optional[Any] = None
#     STUDY_DESIGN_NOTES: Optional[Any] = None
#     DOSE: Optional[Any] = None
#     TREATMENT_PARENT: Optional[Any] = None
#     ORGAN_DETAIL: Optional[Any] = None
#     ORGAN: Optional[Any] = None
#     TREATMENT: Optional[Any] = None
#     CFU: Optional[Any] = None
#     NAME: Optional[Any] = None
#     DOSE_UNITS: Optional[Any] = None
#     SAMPLE_ID: Optional[Any] = None
#     ROUTE: Optional[Any] = None
#     PARENT: Optional[Any] = None
#     Treatment3Route: Optional[Any] = None
#     Treatment3Date: Optional[Any] = None
#     Treatment3Dose: Optional[Any] = None
#     Treatment3DoseUnits: Optional[Any] = None

# class Metadata(BaseModel):
#     Analyte: Optional[str] = None
#     AntibodyParent: Optional[str] = None
#     BioSampleAccession: Optional[str] = None
#     BiosafetyLevel: Optional[str] = None
#     Catalog: Optional[str] = None
#     CellCount: Optional[str] = None
#     CellLine: Optional[str] = None
#     CellLineage: Optional[str] = None
#     Checksum_PrimaryData: Optional[str] = None
#     Checksum_PrimaryType: Optional[str] = None
#     Clone: Optional[str] = None
#     Cohort: Optional[str] = None
#     CompensationFCSParent: Optional[str] = None
#     Concentration: Optional[str] = None
#     ConcentrationUnits: Optional[str] = None
#     ExperimentType: Optional[str] = None
#     File_PrimaryData: Optional[str] = None
#     Fixation: Optional[str] = None
#     Fixative: Optional[str] = None
#     FlowAmount: Optional[str] = None
#     FlowAmountUnits: Optional[str] = None
#     FMO: Optional[str] = None
#     Genotype: Optional[str] = None
#     Instrument: Optional[str] = None
#     InstrumentUser: Optional[str] = None
#     Link_PrimaryData: Optional[str] = None
#     Media: Optional[str] = None
#     Name: Optional[str] = None
#     Notes: Optional[str] = None
#     Parent: Optional[str] = None
#     PassageNum: Optional[str] = None
#     Path_PrimaryData: Optional[str] = None
#     Phenotype: Optional[str] = None
#     Protocol: Optional[str] = None
#     Protocol_Stimulation: Optional[str] = None
#     Protocol_Treatment: Optional[str] = None
#     Publish_uri: Optional[str] = None
#     QC: Optional[str] = None
#     QC_notes: Optional[str] = None
#     ReagenCatalogNum: Optional[str] = None
#     Reagent: Optional[str] = None
#     ReagentBrand: Optional[str] = None
#     ReagentManufacturer: Optional[str] = None
#     Reference: Optional[str] = None
#     Repository: Optional[str] = None
#     RepositoryID: Optional[str] = None
#     Scientist: Optional[str] = None
#     SEEKSubmissionDate: Optional[str] = None
#     SampleCreationDate: Optional[str] = None
#     Software: Optional[str] = None
#     Source: Optional[str] = None
#     SourceFacility: Optional[str] = None
#     Species: Optional[str] = None
#     Stain: Optional[str] = None
#     Stimulation: Optional[str] = None
#     StorageLocation: Optional[str] = None
#     StorageSite: Optional[str] = None
#     StorageTemperature: Optional[str] = None
#     StorageTemperatureUnits: Optional[str] = None
#     StorageType: Optional[str] = None
#     Study: Optional[str] = None
#     Timepoint: Optional[str] = None
#     TotalProtein: Optional[str] = None
#     TotalProteinUnits: Optional[str] = None
#     Treatment1: Optional[str] = None
#     Treatment1Dose: Optional[str] = None
#     Treatment1DoseUnits: Optional[str] = None
#     Treatment1Reference: Optional[str] = None
#     Treatment2: Optional[str] = None
#     Treatment2Dose: Optional[str] = None
#     Treatment2DoseUnits: Optional[str] = None
#     Treatment2Reference: Optional[str] = None
#     TreatmentDoseTime: Optional[str] = None
#     TreatmentRoute: Optional[str] = None
#     TreatmentTimeUnits: Optional[str] = None
#     TreatmentType: Optional[str] = None
#     Type: Optional[str] = None
#     UID: Optional[str] = None
#     ValidationMethod: Optional[str] = None
#     ValidationQuality: Optional[str] = None
#     Vendor: Optional[str] = None

class Metadata(BaseModel):
    UID: str
    Name: Optional[Union[str, int]] = None
    Link_PrimaryData: Optional[str] = None
    # Allow arbitrary additional fields
    class Config:
        extra = "allow"
        
    def __init__(self, **data):
        super().__init__(**data)

# ALLOWED_KEYS = list(Metadata.__annotations__.keys())

class PAVInfo(BaseModel):
    pass

class UpdatePipelineMetadata(BaseModel):
    success: bool
    logs: list[str]
    errors: Optional[list[str]] = None
    stats: dict[str, Any]
