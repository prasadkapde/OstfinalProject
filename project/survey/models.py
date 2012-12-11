from google.appengine.ext import db
class UserData(db.Model):
	user=db.StringProperty()
	voteHistory=db.StringProperty()
	createdSurveyHistory=db.StringProperty()
class Item(db.Model):
        name=db.StringProperty()
        image=db.BlobProperty()
       	survey=db.StringProperty()
	owner=db.UserProperty()
class Survey(db.Model):
	name=db.StringProperty()
	values=db.StringListProperty()
	owner=db.UserProperty()
class Vote(db.Model):
	name=db.StringProperty();
	owner=db.UserProperty();
	survey=db.StringProperty();
	win=db.IntegerProperty();
class VoteValidator(db.Model):
	name=db.StringProperty();
        owner=db.UserProperty();
        survey=db.StringProperty();
        voter=db.UserProperty();	
