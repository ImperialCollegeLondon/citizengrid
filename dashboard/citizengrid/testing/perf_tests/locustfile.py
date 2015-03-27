from locust import HttpLocust, TaskSet, task
import requests.packages.urllib3.contrib.pyopenssl
requests.packages.urllib3.contrib.pyopenssl.inject_into_urllib3()

USER_CREDENTIALS = [
    ("poonam", "poonam"),
    ("admin", "admin")
]

class UserBehavior(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        if len(USER_CREDENTIALS) > 0:
            user, passw = USER_CREDENTIALS.pop()
            self.login(user,passw,verify=False)


    def login(self,user,passw):
        r = self.client.get('')
        self.client.post("/accounts/login/", {"username":"poonam", "password":"poonam",
                                              'csrfmiddlewaretoken': r.cookies['csrftoken']},verify=False)

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

    @task(1)
    def manage_group(self):
        self.client.get("/cg/manage/group",verify=False)

    @task(5)
    def manage_cred(self):
        self.client.get("/cg/manage/cred",verify=False)

    @task(5)
    def manage_images(self):
        for i in range(60,63):
            self.client.get("/cg/manage/images/"+str(i),verify=False)


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait=5000
    max_wait=9000