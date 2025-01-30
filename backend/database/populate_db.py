# populate_db.py

import pandas as pd
from faker import Faker
from typing import Type
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, Any

fake = Faker()

def generate_fake_data(model: Type[BaseModel], num_rows: int = 10) -> pd.DataFrame:
    """
    Generate fake data for a given Pydantic model.

    :param model: Pydantic model class representing the table schema.
    :param num_rows: Number of rows of fake data to generate.
    :return: A pandas DataFrame containing the fake data.
    """
    data = {field: [] for field in model.__annotations__.keys()}

    for _ in range(num_rows):
        for field, field_type in model.__annotations__.items():
            if field == 'first_letter':
                # Generate a single uppercase letter for CHAR(1)
                data[field].append(fake.random_letter().upper())
            elif field_type == Optional[str] or field_type == str:
                # Limit string length to 255 characters for VARCHAR(255)
                data[field].append(fake.text(max_nb_chars=255))
            elif field_type == Optional[int] or field_type == int:
                data[field].append(fake.random_int(min=1, max=100))
            elif field_type == Optional[datetime] or field_type == datetime:
                data[field].append(fake.date_time_this_decade())
            elif field_type == Optional[date] or field_type == date:
                data[field].append(fake.date_this_decade())
            elif field_type == Optional[bool] or field_type == bool:
                data[field].append(fake.boolean())
            else:
                data[field].append(None)  # Default case for unsupported types

    return pd.DataFrame(data)

# dotenv.load_dotenv()

# Debugging: Print environment variables
# print("HOST:", os.getenv('HOST'))
# print("USER:", os.getenv('USER'))
# print("DBNAME:", os.getenv('DBNAME'))
# print("PASSWORD:", os.getenv('PASSWORD'))

# HOST = os.getenv('HOST')
# USER = os.getenv('USER')
# DBNAME = os.getenv('DBNAME')
# PASSWORD = os.getenv('PASSWORD')

# HOST = 'localhost'
# USER = 'mockuser'
# DBNAME = 'mockdb'
# PASSWORD = 'mockpassword'

# fake = Faker()
# conn = psycopg2.connect(
#     host=HOST,
#     dbname=DBNAME,
#     user=USER,
#     password=PASSWORD
# )
# cur = conn.cursor()

# Insert fake data into the 'projects' table
# project_query = """
# INSERT INTO projects (title, web_page, wiki_page, created_at, updated_at, description, avatar_id, default_policy_id, first_letter, site_credentials, site_root_uri, last_jerm_run, uuid, programme_id, default_license, use_default_policy, start_date, end_date)
# VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
# """

# for _ in range(50):
#     cur.execute(project_query, (
#         fake.company(),
#         fake.url(),
#         fake.url(),
#         datetime.now(),
#         datetime.now(),
#         fake.text(),
#         fake.random_int(min=1, max=100),
#         fake.random_int(min=1, max=100),
#         fake.random_letter().upper(),
#         fake.password(),
#         fake.url(),
#         datetime.now(),
#         fake.uuid4(),
#         fake.random_int(min=1, max=100),
#         'CC-BY-4.0',
#         fake.boolean(),
#         fake.date_this_decade(),
#         fake.date_this_decade()
#     ))

# # Insert fake data into the 'samples' table
# sample_query = """
# INSERT INTO samples (title, sample_type_id, json_metadata, uuid, contributor_id, policy_id, created_at, updated_at, first_letter, other_creators, originating_data_file_id, deleted_contributor)
# VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
# """

# for _ in range(50):
#     cur.execute(sample_query, (
#         fake.word(),
#         fake.random_int(min=1, max=100),
#         fake.json(),
#         fake.uuid4(),
#         fake.random_int(min=1, max=100),
#         fake.random_int(min=1, max=100),
#         datetime.now(),
#         datetime.now(),
#         fake.random_letter().upper(),
#         fake.name(),
#         fake.random_int(min=1, max=100),
#         fake.name()
#     ))

# # Commit the transaction
# conn.commit()
# cur.close()
# conn.close()

