#!/bin/bash

# Check if DB_PASSWORD is set
if [ -z "$DB_PASSWORD" ]; then
  echo "Error: DB_PASSWORD environment variable is not set."
  exit 1
fi

mysqldump -u"$DB_USER" -h"$DB_HOST" -p"$DB_PASSWORD" --no-data "$DB_NAME" \
  projects \
  samples \
  projects_samples \
  sample_types \
  projects_sample_types \
  assays \
  studies \
  investigations \
  investigations_projects \
  sops \
  projects_sops \
  institutions \
  work_groups \
  group_memberships \
  people \
  users \
  publications \
  projects_publications \
  assay_assets \
  > partial_schema.sql
