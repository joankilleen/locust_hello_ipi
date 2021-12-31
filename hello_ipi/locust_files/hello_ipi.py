from locust import HttpUser, task

class HelloIPI(HttpUser):
    @task
    def hello_ipi(self):
        self.client.get("/etwas-schuetzen")

    @task
    def test_fail_url(self):
        self.client.get("/nonsense")
