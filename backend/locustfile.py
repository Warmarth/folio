from locust import HttpUser, task, between


class FlaskUser(HttpUser):
    # Simulate users pausing between requests
    wait_time = between(1, 3)

    @task
    def visit_home(self):
        self.client.get("/")