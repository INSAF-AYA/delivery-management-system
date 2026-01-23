from django.urls import path
from . import views

app_name = "agent"

urlpatterns = [
    path("", views.agent_list, name="agent_list"),
    path("add/", views.add_agent, name="add_agent"),
    path("delete/", views.delete_agent, name="delete_agent"),
]
