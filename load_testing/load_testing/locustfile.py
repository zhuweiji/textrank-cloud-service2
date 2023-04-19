from locust import HttpUser, task
import os
import time
import logging
import json

logging.basicConfig(format='%(name)s-%(levelname)s|%(lineno)d:  %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)
class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):

        SLEEP_TIME = 1

        log.info("Making POST Request to /image_transcribe")
        response = self.client.post("/image_transcribe", files=[
          ('images',('test_image2.jpg', open('../../postman/resources/test_image2.jpg','rb'),'image/jpeg'))])

        taskID = response.json()['task_id_list'][0]
        log.info("Task ID: {}".format(taskID))

        # log.info("Waiting {} seconds...".format(SLEEP_TIME))
        # time.sleep(SLEEP_TIME)

        log.info("Making GET Request to /check_task_result")
        response = self.client.get("/check_task_result?task_id={}".format(taskID))
        log.info("Result = {}".format(json.dumps(response.json(), indent = 4)))
