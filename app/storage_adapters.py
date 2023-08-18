""" Storage adapters for the langwizard """
import json
import time
from google.api_core.exceptions import NotFound
from app.bucket import store_blob, fetch_blob


class StorageAdapter:
    """ used by the langwizard to store payloads in databases """

    def store(self, payload_json, keys):
        """ Store a payload in a database with an id keys """
        raise NotImplementedError

    def fetch(self, key):
        """ Get an item in the database based on some keys """
        raise NotImplementedError

class GoogleBucketStorage(StorageAdapter):
    """ Storage bucket adapter for GCP buckets """

    def __init__(self, storage_client, bucket_name):
        self.storage_client = storage_client
        self.bucket_name = bucket_name

    def store(self, payload_json, keys):
        if isinstance(payload_json, dict):
            payload_json = json.dumps(payload_json)
        store_blob(self.storage_client, self.bucket_name, payload_json, keys)

    def fetch(self, key):
        retry = 0
        retry_bool = True
        while retry_bool:
            try:
                return fetch_blob(self.storage_client, self.bucket_name, key)
            except NotFound:
                retry += 1
                if retry > 10:
                    return "There has been an error while retrieving the content used."
                time.sleep(5)
