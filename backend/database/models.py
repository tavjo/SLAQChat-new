from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime, date

class projects(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    web_page: Optional[str] = None
    wiki_page: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    description: Optional[str] = None
    avatar_id: Optional[int] = None
    default_policy_id: Optional[int] = None
    first_letter: Optional[str] = None
    site_credentials: Optional[str] = None
    site_root_uri: Optional[str] = None
    last_jerm_run: Optional[datetime] = None
    uuid: Optional[str] = None
    programme_id: Optional[int] = None
    default_license: str = 'CC-BY-4.0'
    use_default_policy: bool = False
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class samples(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    sample_type_id: Optional[int] = None
    json_metadata: Optional[str] = None
    uuid: Optional[str] = None
    contributor_id: Optional[int] = None
    policy_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    first_letter: Optional[str] = None
    other_creators: Optional[str] = None
    originating_data_file_id: Optional[int] = None
    deleted_contributor: Optional[str] = None

class projects_samples(BaseModel):
    project_id: int
    sample_id: int

class sample_types(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    uuid: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    first_letter: Optional[str] = None
    description: Optional[str] = None
    uploaded_template: bool = False
    contributor_id: Optional[int] = None
    deleted_contributor: Optional[str] = None
    template_id: Optional[int] = None
    other_creators: Optional[str] = None

class projects_sample_types(BaseModel):
    project_id: int
    sample_type_id: int

class assays(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    study_id: Optional[int] = None
    contributor_id: Optional[int] = None
    first_letter: Optional[str] = None
    assay_class_id: Optional[int] = None
    uuid: Optional[str] = None
    policy_id: Optional[int] = None
    assay_type_uri: Optional[str] = None
    technology_type_uri: Optional[str] = None
    suggested_assay_type_id: Optional[int] = None
    suggested_technology_type_id: Optional[int] = None
    other_creators: Optional[str] = None
    deleted_contributor: Optional[str] = None
    sample_type_id: Optional[int] = None
    position: Optional[int] = None
    assay_stream_id: Optional[int] = None

class studies(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    investigation_id: Optional[int] = None
    experimentalists: Optional[str] = None
    begin_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    first_letter: Optional[str] = None
    uuid: Optional[str] = None
    policy_id: Optional[int] = None
    contributor_id: Optional[int] = None
    other_creators: Optional[str] = None
    deleted_contributor: Optional[str] = None
    position: Optional[int] = None

class investigations(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    first_letter: Optional[str] = None
    uuid: Optional[str] = None
    policy_id: Optional[int] = None
    contributor_id: Optional[int] = None
    other_creators: Optional[str] = None
    deleted_contributor: Optional[str] = None
    position: Optional[int] = None
    is_isa_json_compliant: Optional[bool] = None

class investigations_projects(BaseModel):
    project_id: int
    investigation_id: int

class sops(BaseModel):
    id: Optional[int] = None
    contributor_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    version: int = 1
    first_letter: Optional[str] = None
    other_creators: Optional[str] = None
    uuid: Optional[str] = None
    policy_id: Optional[int] = None
    doi: Optional[str] = None
    license: Optional[str] = None
    deleted_contributor: Optional[str] = None

class projects_sops(BaseModel):
    project_id: int
    sop_id: int

class institutions(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    web_page: Optional[str] = None
    country: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    avatar_id: Optional[int] = None
    first_letter: Optional[str] = None
    uuid: Optional[str] = None

class work_groups(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    institution_id: Optional[int] = None
    project_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class group_memberships(BaseModel):
    id: Optional[int] = None
    person_id: Optional[int] = None
    work_group_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    time_left_at: Optional[datetime] = None
    has_left: bool = False

class people(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skype_name: Optional[str] = None
    web_page: Optional[str] = None
    description: Optional[str] = None
    avatar_id: Optional[int] = None
    status_id: int = 0
    first_letter: Optional[str] = None
    uuid: Optional[str] = None
    roles_mask: int = 0
    orcid: Optional[str] = None

class users(BaseModel):
    id: Optional[int] = None
    login: Optional[str] = None
    crypted_password: Optional[str] = None
    salt: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    remember_token: Optional[str] = None
    remember_token_expires_at: Optional[datetime] = None
    activation_code: Optional[str] = None
    activated_at: Optional[datetime] = None
    person_id: Optional[int] = None
    reset_password_code: Optional[str] = None
    reset_password_code_until: Optional[datetime] = None
    posts_count: int = 0
    last_seen_at: Optional[datetime] = None
    uuid: Optional[str] = None

class publications(BaseModel):
    id: Optional[int] = None
    pubmed_id: Optional[int] = None
    title: Optional[str] = None
    abstract: Optional[str] = None
    published_date: Optional[date] = None
    journal: Optional[str] = None
    first_letter: Optional[str] = None
    contributor_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    doi: Optional[str] = None
    uuid: Optional[str] = None
    policy_id: Optional[int] = None
    citation: Optional[str] = None
    deleted_contributor: Optional[str] = None
    registered_mode: Optional[int] = None
    booktitle: Optional[str] = None
    publisher: Optional[str] = None
    editor: Optional[str] = None
    publication_type_id: Optional[int] = None
    url: Optional[str] = None
    version: int = 1
    license: Optional[str] = None
    other_creators: Optional[str] = None

class projects_publications(BaseModel):
    project_id: int
    publication_id: int

class assay_assets(BaseModel):
    id: Optional[int] = None
    assay_id: Optional[int] = None
    asset_id: Optional[int] = None
    version: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    relationship_type_id: Optional[int] = None
    asset_type: Optional[str] = None
    direction: int = 0

