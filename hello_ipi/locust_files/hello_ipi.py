import random
import logging
import sys
from locust import between, task, HttpUser
from pyquery import PyQuery

class HelloIPI(HttpUser):
    
    wait_time = between(10, 600)
    

    def on_start(self):      
        self.hello_ipi()
        self.urls_on_current_page = self.urls_found
        print("Urls found: " + str(len(self.urls_on_current_page)))
        
    

    def hello_ipi(self):
        request = self.client.get("")
        my_query = PyQuery(request.content)

        # Find other links on the page
        link_elements = my_query(".ige_teasertopimage_teaser a")
        self.urls_found = [
            l.attrib["href"] for l in link_elements
        ]

    @task
    def load_page(self):
        url = random.choice(self.urls_on_current_page)
        r = self.client.get(url)

    
