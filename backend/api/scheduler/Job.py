
from uuid import uuid4, UUID
import time
import sys

from api.scheduler.JobDb import *


# Tests if a given uuid string (uuid_to_test) is a valid uuid4.
def is_valid_jobid(val):
    try:
        UUID(str(val))
        return True
    except ValueError:
        return False


class Job:
    # Creates a new Job with a random id.
    def __init__(self, shot_parameter, shot_length, video_location, output_location, insert_to_db=True):
        self.id = str(uuid4())
        self.shot_parameter = shot_parameter
        self.shot_length = shot_length
        self.video_location = video_location
        self.output_location = output_location

        self.status = JobStatusTypes.Created
        self.timestamps = {JobStatusTypes.Created: 0.0, JobStatusTypes.Processing: 0.0,
                           JobStatusTypes.Transcoding: 0.0, JobStatusTypes.Completed: 0.0}
        self.update_timestamp(JobStatusTypes.Created)

        # Insert job into database.
        if insert_to_db:
            insert_job_to_db(self.id, shot_parameter, shot_length, video_location,
                    output_location, self.timestamps[JobStatusTypes.Created])

    def empty():
        return Job(0.0, 0.0, "", "", insert_to_db=False)

    # Sets the current status to the provided status and stores a timestamp for
    # when the change occurred.
    def update_status(self, status_type):
        self.status = status_type
        self.update_timestamp(status_type)

        update_job_status_db(self.id, status_type)

    # Sets the timestamp for a given status type to the provided time. If no
    # specific time was provided, the current timestamp is used.
    def update_timestamp(self, status_type, timestamp=0):
        if timestamp == 0:
            timestamp = time.time()

        self.timestamps[status_type] = timestamp
        update_job_timestamp_db(self.id, status_type, timestamp)

    # Returns the difference between two timestamps for the Job. If at least one
    # of the timestamps is not stored, -1 is returned.
    def get_time_difference(self, timestamp_begin, timestamp_end):

        if timestamp_begin not in self.timestamps or timestamp_end not in self.timestamps:
            return -1

        return self.timestamps[timestamp_end] - self.timestamps[timestamp_begin]

    # Fetches a Job from the database given a job id. If a job with that id does
    # not exist, None is returned.
    def from_database(id):

        job = Job.empty()
        db_job = get_job(id)

        if db_job is None:
            return None

        job.id = db_job["id"]
        job.shot_parameter = db_job["shot_parameter"]
        job.shot_length = db_job["shot_length"]
        job.video_location = db_job["video_location"]
        job.output_location = db_job["output_location"]

        job.status = JobStatusTypes.from_str(db_job["status"])
        job.timestamps[JobStatusTypes.Created] = db_job["time_created"]
        job.timestamps[JobStatusTypes.Processing] = db_job["time_processing"]
        job.timestamps[JobStatusTypes.Transcoding] = db_job["time_transcoding"]
        job.timestamps[JobStatusTypes.Completed] = db_job["time_completed"]

        return job
