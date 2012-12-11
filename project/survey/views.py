from survey import app
from survey.models import Survey
from survey.models import Item
from survey.models import Vote
from survey.models import VoteValidator
from flask import request, render_template, redirect, flash, url_for
import cgi
import cgitb
from google.appengine.ext import db
from google.appengine.api import users
cgitb.enable();

@app.route('/index')
def index():
	return render_template('index.html',data="Welcome!")

@app.route('/')
def index():
        return render_template('index.html',data="Welcome!")

@app.route('/startup')
def startup():
	form = cgi.FieldStorage();
	if (form['startup'].value == "create"):
		return render_template('survey.html');
	if (form['startup'].value == "listmysurvey"):
                user = users.get_current_user();
	        surveys = db.GqlQuery("SELECT * FROM Survey WHERE owner = :1",user);
		listOfSurveys = [];
		for sur in surveys:
			name1 = sur.name+" by " + str(user);
			listOfSurveys.append(name1);
        	return render_template('listsurveys.html',surveys=listOfSurveys,for_user=user,path="vote");
	if (form['startup'].value == "listallsurvey"):
                user = users.get_current_user();
                surveys = db.GqlQuery("SELECT * FROM Survey");
                listOfSurveys = [];
                for sur in surveys:
			val = sur.name+" by " + str(sur.owner);
                        listOfSurveys.append(val);
                return render_template('listsurveys.html',surveys=listOfSurveys,for_user="All Users",path="vote");
	if (form['startup'].value == "delete"):
		db.delete(db.Query());
		return 'done';
	if (form['startup'].value == "addItems"):
		user = users.get_current_user();
		surveys = db.GqlQuery("SELECT * FROM Survey WHERE owner = :1",user);
                listOfSurveys = [];
                for sur in surveys:
                        name1 = sur.name+" by " + str(user);
                        listOfSurveys.append(name1);
		return render_template('listsurveys.html',surveys=listOfSurveys,for_user=str(user),path="add");
	if (form['startup'].value == "delItems"):
                user = users.get_current_user();
                surveys = db.GqlQuery("SELECT * FROM Survey WHERE owner = :1",user);
                listOfSurveys = [];
                for sur in surveys:
                        name1 = sur.name+" by " + str(user);
                        listOfSurveys.append(name1);
                return render_template('listsurveys.html',surveys=listOfSurveys,for_user=str(user),path="delete");
			
@app.route('/addsurvey')
def addSurvey():
	form = cgi.FieldStorage();
	user = users.get_current_user();
	surveyName = form['sname'].value;	
	rawOptions = form['options'].value;
	rawOptions += ',';
	optionList = rawOptions.split(',');
	surveys = db.GqlQuery("SELECT * FROM Survey WHERE name = :1 and owner = :2",surveyName,user);
	counter = surveys.count();
	if (counter == 0):
		survey = Survey(name=surveyName);
		survey.values = optionList;
		survey.owner = user;
		survey.put();
		for option in optionList:
			if option:
				item = Item(name=option);
				item.survey = surveyName;
				item.owner = user;
				item.put();
		return render_template('survey_confirmation.html',survey=surveyName,option=optionList);
	else:
		return render_template('failure.html',message="You already have created this survey! Please create a different survey.");
		

@app.route('/listmysurveys')
def listMySurveys():
	user = users.get_current_user();
	surveys = db.GqlQuery("SELECT * FROM Survey WHERE owner = :1",user);
	return render_template('mysurveys.html',surveys=surveys);

@app.route('/generatevotingpage')
def generateVotingPage():
	form = cgi.FieldStorage();
	path="vote";
	if (form.has_key("delete")):
		path="delete";
	rawOption = form['voteon'].value;
	optionList = rawOption.split("__by__");
	#_ote('listsurveys.html',surveys=listOfSurveys,for_user="All Users",path=vote);iptionList[1];
	surveyName = optionList[0].replace("__"," ");
	user = users.User(optionList[1]);
	itemList = db.GqlQuery("SELECT * FROM Item WHERE survey = :1 and owner = :2",surveyName,user);
	options = [];
	for i in itemList:
		options.append(i.name);
	return render_template('voting.html',surveys=optionList[0],user=user,options=options,path=path);

@app.route('/registervote')
def registerVote():
	form = cgi.FieldStorage();
	voteon = form['voteon'].value;
	vote = voteon.replace("__"," ");
	survey = form['survey'].value;
	user = form['user'].value;
	user1 = users.User(user);
	voter = users.get_current_user();
	isvoted = db.GqlQuery("SELECT * FROM VoteValidator WHERE survey = :1 and owner = :2 and voter = :3",survey,user1,voter);
	counter = isvoted.count();
	if ( counter == 0 ):
		winnerVote = db.GqlQuery("SELECT * FROM Vote WHERE owner = :1 and survey = :2 and name = :3",user1,survey,vote);
		win_number = 1;
		for i in winnerVote:
			win_number = i.win;
			win_number += 1;
		db.delete(winnerVote);
		newVote = Vote(name=vote,survey=survey,owner=user1,win=win_number);
		newVote.put();
		voteValidator = VoteValidator(name=vote,survey=survey,owner=user1,voter=voter);
		voteValidator.put();		
		return render_template('successful_voting.html',winner=vote,looser=" All Others.");
	else:
		return render_template('failure.html',message="You already have voted this survey!");

@app.route('/viewresults')
def viewResults():
	form = cgi.FieldStorage();
	survey = form['survey'].value;
        user = form['user'].value;
	owner = users.User(user);
	items = db.GqlQuery("SELECT * FROM Item WHERE survey = :1 and owner = :2",survey,owner);
	voteList = [];
	for item in items:
		winNumber = 0;
		win_count = db.GqlQuery("SELECT * FROM Vote WHERE name = :1 and survey = :2 and owner = :3",item.name,survey,owner);
		for win1 in win_count:
			winNumber = win1.win;
		resultString = item.name +"###" +str(winNumber);
		voteList.append(resultString);
	return render_template('results.html',results=voteList);

@app.route('/addItems')
def addItems():
	return "add";

@app.route('/deleteItem')
def deleteItem():
	form = cgi.FieldStorage();
	vote = form['voteon'].value;	
        item = vote.replace("__"," ");
	survey = form['survey'].value;	
	owner = users.get_current_user();
	oldSurvey = db.GqlQuery("SELECT * FROM Survey WHERE name = :1 and owner = :2",survey,owner);
	oldValues = [];
	for sur in oldSurvey:
		print "in";
		print sur.name;
		oldValues = sur.values;
	print survey + "<br>";
	print str(owner) + "<br>";
	print item;
	oldValues.remove(item);
	newSurvey = Survey(name=survey,owner=owner,values=oldValues);
	db.delete(oldSurvey);
	newSurvey.put();
	oldItem = db.GqlQuery("SELECT * FROM Item WHERE name = :1 and owner = :2 and survey = :3",item,owner,survey);
	db.delete(oldItem);
	return render_template('survey_confirmation.html',survey=survey,option=oldValues);	
