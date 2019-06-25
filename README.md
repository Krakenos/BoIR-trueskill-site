# The Binding of Isaac: Rebirth Tournament Leaderboards

This is a repository for [isaac rankings site](https://isaacrankings.com/) that contains leaderboards which main purpose is to be a seeding method for racing tournaments for *[The Binding of Isaac: Rebirth](http://store.steampowered.com/app/250900/The_Binding_of_Isaac_Rebirth/)*. Algorithm used to calculate ratings is [TrueSkill](https://www.microsoft.com/en-us/research/wp-content/uploads/2007/01/NIPS2006_0688.pdf)

Furthermore, by using the [TrueSkill algorithm](https://www.microsoft.com/en-us/research/wp-content/uploads/2007/01/NIPS2006_0688.pdf) on every 1v1 matchup, we can create a leaderboard for the top players.

<br />

## Installing local development environment

* In order to install development environment you need to have installed Python 3.6+.

* If you already have that installed and cloned this repository, next step is to download all the requirements:
   * `$ pip install -r requirements`

* Next step is to setup your .env, the following settings work great for the purpose of local environment.

```
   CHALLONGE_API_KEY=your-api-key
   SECRET_KEY=some-secret-key
   DEBUG=True
   SECURE_SSL_REDIRECT=False
   SESSION_COOKIE_SECURE=False
   CSRF_COOKIE_SECURE=False
```
   
*NOTE: CHALLONGE_API_KEY is not being used yet*

* Then you will have to migrate your database to work with django models, and fill it with data. To do so run the following commands in the main directory of cloned project.
   * `$ python manage.py migrate`
   * `$ python manage.py import_json --bulk --adduser`

* To run debug server simply type:
   * `$ python manage.py runserver`
