from plyer import notification
from requests import RequestException, ConnectionError, ConnectTimeout
from requests_html import HTMLSession
from platformdirs import user_cache_dir
import pickle
import time
import os

session = HTMLSession()
projects = []

appname = "Mostaql Notifier"
appauthor = "Mohammed Alnahall"

cache_dir = user_cache_dir(appname, appauthor) + "/projects_cache"

os.makedirs(os.path.dirname(cache_dir), exist_ok=True)

try:
  with open(cache_dir, "rb") as projects_cache:
    if(os.path.getsize(cache_dir) > 0):
      projects = pickle.load(projects_cache)
except OSError:
  open(cache_dir, "x")

# change the following to fit your needs
config = {
  "category" : "business,development,engineering-architecture,design,marketing,writing-translation,support,training",
  "budget_min" : 25, # should be one of the following => 25,50,100,250,500,1000,2500,5000,10000
  "budget_max" : 10000, # should be one of the following => 25,50,100,250,500,1000,2500,5000,10000
  "duration" : "0-6,7-14,15-30,31-90,91-100000"
}

while True:
  try:
    response = session.get("https://mostaql.com/projects", params=config)

    html_projects = response.html.find('.project-row')     
    for html_project in reversed(html_projects):
      title_anchor = html_project.find('.mrg--bt-reset', first=True).find('a', first=True)
      project = {
        "title":title_anchor.text,
        "breif":html_project.find('p.project__brief', first=True).text
      }

      try:
        projects.index(project)
        continue
      except ValueError:                      
        time.sleep(1)    
        project_page = session.get(title_anchor.attrs["href"])
        budget_range = project_page.html.find('td[data-type="project-budget_range"]', first=True).find('span', first=True).text
        notification.notify(
          title = project["title"][0:63],
          message = (budget_range + " " + project["breif"])[0:255],
          app_name ="Mostaql Notifier",
          app_icon = None,
          timeout = None,
        )

        projects.append(project)

    projects = projects[max(0,len(projects)-25):len(projects)]

    with open(cache_dir, "wb") as projects_cahche:
      pickle.dump(projects, projects_cahche)

  except ConnectTimeout:
    notification.notify(
        title = 'Mostaql Notifier Error',
        message = 'Timeout Error',
        app_name ="Mostaql Notifier",
        app_icon = None,
        timeout = 10,
        )
  except ConnectionError:
    notification.notify(
        title = 'Mostaql Notifier Error',
        message = 'Connection Error',
        app_name ="Mostaql Notifier",
        app_icon = None,
        timeout = 10,
        )
  except RequestException:
    notification.notify(
        title = 'Mostaql Notifier Error',
        message = 'Coudn\'t handle request',
        app_name ="Mostaql Notifier",
        app_icon = None,
        timeout = 10,
        )
  except Exception as e:
    print(e)
    notification.notify(
        title = 'Mostaql Notifier Error',
        message = 'Somthing Went Wrong!!',
        app_name ="Mostaql Notifier",
        app_icon = None,
        timeout = 10,
        )
  time.sleep(60)