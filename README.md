# The RLP

Designed with research libraries and archives in mind, the RLP is a web application for library staff to easily manage day-to-day front desk operations. Staffers can log in and handle visitor check-in and check-out, track resources loaned to visitors, handle appointment requests and register new visitors.

Visitor check-in is easy, as well as seeing a list of all visitors currently checked in.

![Alt Text](https://gph.is/2BLhwUO)

<img src="https://gph.is/2BLhwUO" title="Checkin visitor">

<iframe src="https://giphy.com/embed/pOTF0pwczuoiJbMuhz" width="480" height="244" frameBorder="0" class="giphy-embed" allowFullScreen></iframe><p><a href="https://giphy.com/gifs/visitor-check-in-pOTF0pwczuoiJbMuhz">via GIPHY</a></p>

Library staff can easily look up resources and associate it to a visitor.

<img src="https://j.gifs.com/L8rg5g.gif" title="Lookup book and add">

The system checks to make sure that a visitor does not have any unreturned items before check out.

<img src="https://j.gifs.com/E9klPk.gif" title="Checkout denied">

The app also allows for limited log in privileges for visitors to quickly look up their past reference materials and make appointment requests with library staff.

<img src="https://j.gifs.com/RoAgw0.gif" title="Visitor log in view">

## Getting Started

How to quickly get this sucker up and running on your local for development and testing.

### Prerequisites

* Requires Google Calendar. Get API credentials [here](https://developers.google.com).

Install the requirements to your enviroment.

```
$ pip install -r requirements.txt
```

Google credentials should be set to an environmental variable.

```
export GOOGLE_CAL_APP_CREDENTIALS='secretkeyhere'
```

```APPLICATION_NAME``` should be set to your project name on the Google Developer Console.

### Data

The database is powered by PostgreSQL. The initial users are mock data generated on Mockaroo. The books data was pulled from a sample set from the Brooklyn Public Library.

To initialize:

```
$ createdb [name of db]
$ python seed.py
```

Modify the ```model.py``` helper function ```connect_to_db()``` where the ```app.config['SQLALCHEMY_DATABASE_URI']``` point to your database name.

Books loaded to database should be saved to a .CSV file with no headers. User data should be in JSON format. Refer to ```seed.py``` for what fields are needed. Modify ```load_books()``` and ```load_users``` to point to your data files.

## Tech Stack

* Python
* SQLAlchemy
* Javascript
* Flask
* PostgreSQL
* Jinja
* jQuery
* AJAX
* Bootstrap
* HTML/CSS

## APIs Used

* [Google Calendar](https://developers.google.com/google-apps/calendar)
* Brooklyn Public Library (example data)

## Developer

Lives in San Francisco. [Gots the LinkedIn, too.](https://www.linkedin.com/in/myrnaalcaide)
