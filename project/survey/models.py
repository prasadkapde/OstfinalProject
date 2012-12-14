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
		expiration=db.DateTimeProperty()
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
class UploadData(db.Model):
		data=db.BlobProperty();
class Comments(db.Model):
		itemName=db.StringProperty();
		itemOwner=db.UserProperty();
		survey=db.StringProperty();
		comment=db.StringProperty();
class CommentValidator(db.Model):
		itemName=db.StringProperty();
		itemOwner=db.UserProperty();
		survey=db.StringProperty();
		commenter=db.UserProperty();
class Search(db.Model):
		name=db.StringProperty();
		entityType=db.StringProperty();
		survey=db.StringProperty();
		owner=db.UserProperty();
