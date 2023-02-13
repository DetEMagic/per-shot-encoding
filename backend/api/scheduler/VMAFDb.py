
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
class VMAFStatusTypes(str, Enum):
    Computing = "computing",
    Completed = "completed",
    Failed = "failed",

    @staticmethod
    def from_str(label):
        if label == "computing":
            return VMAFStatusTypes.Computing
        elif label == "completed":
            return VMAFStatusTypes.Completed
        elif label == "failed":
            return VMAFStatusTypes.Failed
        else:
            raise NotImplementedError


VMAF_TABLE = "vmaf_scores"

VMAF_TABLE_SQL = f'''CREATE TABLE IF NOT EXISTS {VMAF_TABLE} (
    id                                CHAR(36),
    status                            TEXT,
    score                             FLOAT,
    PRIMARY KEY(id)
)'''

CREATE_VMAF_SQL = f"INSERT INTO {VMAF_TABLE} VALUES (%s, '{VMAFStatusTypes.Computing}', 0.0)"

GET_VMAF_SQL = f"SELECT * FROM {VMAF_TABLE} WHERE id = %s"

UPDATE_STATUS_VMAF_SQL = f"UPDATE {VMAF_TABLE} SET status = %s WHERE id = %s"
UPDATE_SCORE_VMAF_SQL = f"UPDATE {VMAF_TABLE} SET score = %s WHERE id = %s"


# Creates the table where all VMAF scores are stored. Should be called on every start
# of the server.
def create_vmaf_db():
    db_cur.execute(VMAF_TABLE_SQL)
    db.commit()


# Inserts a new VMAF metric to the database.
def insert_vmaf_db(job_id):
    db_cur.execute(CREATE_VMAF_SQL, (job_id,))
    db.commit()


# Retrieves a specific job from the database.
def get_vmaf_db(job_id):
    db_cur.execute(GET_VMAF_SQL, (job_id,))
    result = db_cur.fetchone()
    return result


# Updates the timestamp of a job with a given timestamp
def update_vmaf_status_db(job_id, status_type):
    db_cur.execute(UPDATE_STATUS_VMAF_SQL, (status_type, job_id))
    db.commit()


# Updates the timestamp of a job with a given timestamp
def update_vmaf_score_db(job_id, score):
    db_cur.execute(UPDATE_SCORE_VMAF_SQL, (score, job_id))
    db.commit()
