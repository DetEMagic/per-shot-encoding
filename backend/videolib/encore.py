"""
This class is used to communicate with SVT:s Encore API

For documentation about the functions go to 
https://svt.github.io/encore-doc/openapi.html

"""
import requests

class Encore:

    failed_return = False
    reqExc_msg = "Bad request"

    def __init__(self, url):
        self.url = url


    def create_job(self, data):
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(f"{self.url}/encoreJobs", json=data, headers=headers)

            if response.status_code != 201:
                return self.failed_return
            
            return response.json()
            
        except requests.exceptions.Timeout as e:
            print("Request timed out", e)
            #maybe retry after 10 seconds
            #self.create_job(data)
        except requests.exceptions.RequestException as e:
            print(self.reqExc_msg, e)
    

    def get_job(self, id):
        try:
            response = requests.get(f"{self.url}/encoreJobs/{id}")

            if response.status_code != 200:
                return self.failed_return
            
            return response.json()

        except requests.exceptions.RequestException as e:
            print(self.reqExc_msg, e)
    
    
    def get_jobs(self, page=0, size=20, sort="ASC"):
        try:
            response = requests.get(f"{self.url}/encoreJobs?page={page}&size={size}&sort={sort}")
            
            if response.status_code != 200:
                return self.failed_return

            return response.json()

        except requests.exceptions.RequestException as e:
            print(self.reqExc_msg, e)

    
    def find_job_by_status(self, status="QUEUED", page=0, size=20, sort="ASC"):
        try:
            response = requests.get(f"{self.url}/encoreJobs/search/findByStatus?page={page}&size={size}&sort={sort}&status={status}")

            if response.status_code != 200:
                return self.failed_return
            
            return response.json()

        except requests.exceptions.RequestException as e:
            print(self.reqExc_msg, e)
 

    def update_job(self, id, data):
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.put(f"{self.url}/encoreJobs/{id}", json=data, headers=headers)

            if response.status_code == 204:
                return response.text

            if response.status_code < 200 or response.status_code > 201:
                return self.failed_return
            
            return response.json()

        except requests.exceptions.RequestException as e:
            print(self.reqExc_msg, e)


    def delete_job(self, id):
        try:
            response = requests.delete(f"{self.url}/encoreJobs/{id}")

            if response.status_code != 204:
                return self.failed_return
            
            return response.text

        except requests.exceptions.RequestException as e:
            print(self.reqExc_msg, e)


    def patch_job(self, id, data):
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.patch(f"{self.url}/encoreJobs/{id}", json=data, headers=headers)

            if response.status_code == 204:
                return response.text

            if response.status_code != 200:
                return self.failed_return
            
            return response.json()

        except requests.exceptions.RequestException as e:
            print(self.reqExc_msg, e)


    def cancel_job(self, id):
        try:
            response = requests.post(f"{self.url}/encoreJobs/{id}/cancel")

            if response.status_code != 200:
                return self.failed_return

            return response.text

        except requests.exceptions.RequestException as e:
            print(self.reqExc_msg, e)

    
    def get_queue(self):
        try:
            response = requests.get(f"{self.url}/queue")

            if response.status_code != 200:
                return self.failed_return
            
            return response.json()

        except requests.exceptions.RequestException as e:
            print(self.reqExc_msg, e)

    
