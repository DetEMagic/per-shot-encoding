
from enum import Enum
import yaml
import mysql.connector

config = yaml.safe_load(open("../config.yml"))["db"]

db = mysql.connector.connect(
    host=config["host"],
    user=config["user"],
    password=config["password"],
    database=config["database"]
)

# dictionary=True makes sure that any SELECT statements returns labeled data.
db_cur = db.cursor(dictionary=True)


# Represents the different types of statuses where a Job might be.
class JobStatusTypes(str, Enum):
    Created = "created",
    Processing = "processing",
    Transcoding = "transcoding",
    Completed = "completed"

    @staticmethod
    def from_str(label):
        if label == "created":
            return JobStatusTypes.Created
        elif label == "processing":
            return JobStatusTypes.Processing
        elif label == "transcoding":
            return JobStatusTypes.Transcoding
        elif label == "completed":
            return JobStatusTypes.Completed
        else:
            raise NotImplementedError


JOB_TABLE = "jobs"

JOB_TABLE_SQL = f'''CREATE TABLE IF NOT EXISTS jobs (
    id                                CHAR(36),
    status                            TEXT,
    shot_parameter                    FLOAT,
    shot_length                       FLOAT,
    video_location                    TEXT,
    output_location                   TEXT,
    time_{JobStatusTypes.Created}     INT,
    time_{JobStatusTypes.Processing}  INT,
    time_{JobStatusTypes.Transcoding} INT,
    time_{JobStatusTypes.Completed}   INT,
    PRIMARY KEY(id)
)'''

CREATE_JOB_SQL = f"INSERT INTO {JOB_TABLE} VALUES (%s, '{JobStatusTypes.Created}', %s, %s, %s, %s, %s, 0.0, 0.0, 0.0)"

GET_JOB_SQL = f"SELECT * FROM {JOB_TABLE} WHERE id = %s"

GET_ALL_JOBS_SQL = f"SELECT * FROM {JOB_TABLE}"
GET_ACTIVE_JOBS_SQL = f"SELECT * FROM {JOB_TABLE} WHERE status != '{JobStatusTypes.Completed}'"
GET_COMPLETED_JOBS_SQL = f"SELECT * FROM {JOB_TABLE} WHERE status = '{JobStatusTypes.Completed}'"

UPDATE_STATUS_SQL = f"UPDATE {JOB_TABLE} SET status = %s WHERE id = %s"


# Executes a given SQL statement and returns the value from fetchall()
def execute_sql_and_fetchall(statement):
    db_cur.execute(statement)
    return db_cur.fetchall()


# Creates the table where all jobs are stored. Should be called on every start
# of the server.
def create_job_table_db():
    db_cur.execute(JOB_TABLE_SQL)
    db.commit()


# Inserts a new job to the database.
def insert_job_to_db(id, shot_param, shot_length, video_loc, output_loc, time_created):
    db_cur.execute(CREATE_JOB_SQL, (id, shot_param, shot_length,
                   video_loc, output_loc, time_created))
    db.commit()


# Retrieves a specific job from the database.
def get_job(job_id):
    db_cur.execute(GET_JOB_SQL, (job_id,))
    result = db_cur.fetchone()
    return result


# Returns all jobs
def get_all_jobs():
    return execute_sql_and_fetchall(GET_ALL_JOBS_SQL)


# Returns all jobs that are not marked as "completed".
def get_active_jobs():
    return execute_sql_and_fetchall(GET_ACTIVE_JOBS_SQL)


# Returns all jobs that are marked as "completed".
def get_completed_jobs():
    return execute_sql_and_fetchall(GET_COMPLETED_JOBS_SQL)


# Updates the timestamp of a job with a given timestamp
def update_job_status_db(job_id, status_type):
    db_cur.execute(UPDATE_STATUS_SQL, (status_type, job_id))
    db.commit()


# Updates the timestamp of a job with a given timestamp
def update_job_timestamp_db(job_id, type, timestamp):
    db_cur.execute(
        f"UPDATE {JOB_TABLE} SET time_{type} = %s WHERE id =  %s", (timestamp, job_id))
    db.commit()
