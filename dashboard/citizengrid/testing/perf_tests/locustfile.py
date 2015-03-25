from locust import HttpLocust, TaskSet, task
import requests.packages.urllib3.contrib.pyopenssl
requests.packages.urllib3.contrib.pyopenssl.inject_into_urllib3()

class UserBehavior(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        self.login()

    def login(self):
        self.client.post("/", {"username":"admin", "password":"admin"},verify=False)

    @task(2)
    def index(self):
        self.client.get("/",verify=False)

    @task(1)
    def dashboard(self):
        self.client.get("/cg",verify=False)


    @task(1)
    def contact(self):
        self.client.get("/contact",verify=False)

    @task(1)
    def about(self):
        self.client.get("/about",verify=False)

    @task(1)
    def docs(self):
        self.client.get("/docs",verify=False)

    @task(1)
    def update_act(self):
        self.client.get("/cg/manage/updateaccount",verify=False)

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait=5000
    max_wait=9000