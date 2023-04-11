# screener

----------
 is a screener website that allow you to view the basic information of a company
 the company is searched by it's ticker and the information is gathered from yahoo finance
 the information is taken thanks to the yahooquery library 
 the informations are stored in a database, everytime a ticker is searched the info are 
 stored in the db if they are not already present. if they are the basic infos are taken 
 from the db and updated to the current date.

## Quick start

this app is used inside the project NotFinancialAdvice and it need the following steps to be installed:
 
 0. clone the repo inside the Django project and change the name of the app from NFA_screener to screener

 1. inside settings.py insert 'screener' in the INSTALLED_APPS list
       
    ```
    INSTALLED_APPS = [
        ...
        'screener',
    ]
    ```
 2. run the script archive_creator.sh inside the app to create the folder necessary to hold the files
 3. call the collectstatic from manage.py
 4. include the url.py file inside the app in the main project you may want to add some url path inside the ''
        path('', include(('screener.urls', 'screener'), namespace="screener")),
 5. call the makemigrations / migrate from manage.py Run ``python manage.py migrate screener`` to create the screener models.

 6. Start the development server and visit http://127.0.0.1:8000/admin/
   to create the models (you'll need the Admin app enabled).

 7. Visit http://127.0.0.1:8000 to see the website


## the app use the following libraries:
 1. pandas
 2. numpy
 3. yahooquery

be sure to have them in the virtual env

-----------

# screneer docs                       
if you want to use the URL links outside the app you need to use the namespace.
it is always a good idea when having many apps inside a Django project to use the namespace.
for example:

    > <a href="{% url 'screener:URL' %}"</a>

