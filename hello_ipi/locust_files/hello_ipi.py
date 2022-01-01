import random
import logging
import sys
from locust import between, task, HttpUser
from pyquery import PyQuery

class HelloIPI(HttpUser):

    # we assume someone who is browsing the page, 
    # generally has a quite long waiting time (between 
    # 10 and 600 seconds), since there's a bunch of text 
    # on each page
    wait_time = between(10, 600)
    

    def on_start(self):
        # Set root logging
        logging.getLogger().setLevel('INFO')

        # Add stdout to locust logging
        logger = logging.getLogger('locust')
        logger.addHandler(logging.StreamHandler(sys.stdout))
        
        
        self.hello_ipi()
        self.urls_on_current_page = self.urls_found
        #logging.info("Urls found: " + str(len(self.urls_on_current_page)))
        
    
    
    @task
    def hello_ipi(self):
        request = self.client.get("")
        my_query = PyQuery(request.content)

        # Find other links on the page
        link_elements = my_query(".ige_teasertopimage_teaser a")
        self.urls_found = [
            l.attrib["href"] for l in link_elements
        ]

    @task(5)
    def load_page(self):
        url = random.choice(self.urls_on_current_page)
        r = self.client.get(url)

    
