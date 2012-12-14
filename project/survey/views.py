from survey import app
from survey.models import Survey
from survey.models import Item
from survey.models import Vote, Comments, CommentValidator, Search
from survey.models import VoteValidator
from survey.models import UploadData
from flask import request, render_template, redirect, flash, url_for
from flask import Response
import cgi
import cgitb
import re
import datetime;
from google.appengine.ext import db
from google.appengine.api import users
import xml.dom.minidom
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
	if (form['startup'].value == "listallsurvey" or form['startup'].value == "download"):
                user = users.get_current_user();
                surveys = db.GqlQuery("SELECT * FROM Survey");
                listOfSurveys = [];
                for sur in surveys:
			val = sur.name+" by " + str(sur.owner);
                        listOfSurveys.append(val);
		if (form['startup'].value == "listallsurvey"):
	                return render_template('listsurveys.html',surveys=listOfSurveys,for_user="All Users",path="vote");
		else:
			return render_template('listsurveys.html',surveys=listOfSurveys,for_user="All Users",path="download");
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
	if (form['startup'].value == "upload"):			
		return render_template('upload.html');

@app.route('/addsurvey')
def addSurvey():
	form = cgi.FieldStorage();
	user = users.get_current_user();
	surveyName = form['sname'].value;	
	rawOptions = form['options'].value;
	rawOptions += ',';
	optionList = rawOptions.split(',');
	expireDate = form['dateValue'].value;
	expireHour = int(form['hours'].value);
	expireMinutes = int(form['minutes'].value);
	expireSeconds = int(form['seconds'].value);
	rawDate = expireDate.split("/");
	month = int(rawDate[0]);
	day = int(rawDate[1]);
	year = int(rawDate[2]);
	surveyExpireDate = datetime.datetime(year,month,day,expireHour,expireMinutes,expireSeconds);
	surveys = db.GqlQuery("SELECT * FROM Survey WHERE name = :1 and owner = :2",surveyName,user);
	counter = surveys.count();
	if (counter == 0):
		survey = Survey(name=surveyName,expiration=surveyExpireDate);
		survey.values = optionList;
		survey.owner = user;
		survey.put();
		search = Search(name=surveyName,entityType="survey",survey=surveyName,owner=user);
		search.put();
		for option in optionList:
			if option:
				item = Item(name=option);
				item.survey = surveyName;
				item.owner = user;
				item.put();
				search1 = Search(name=option,entityType="item",survey=surveyName,owner=user);
				search1.put();
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
	surveyName = optionList[0].replace("__"," ");
	user = users.User(optionList[1]);
	itemList = db.GqlQuery("SELECT * FROM Item WHERE survey = :1 and owner = :2",surveyName,user);
	options = [];
	for i in itemList:
		options.append(i.name);
	return render_template('voting.html',surveys=surveyName,user=user,options=options,path=path);

@app.route('/registervote')
def registerVote():
	form = cgi.FieldStorage();
	if(form.has_key('vote')):
		voteon = form['voteon'].value;
		vote = voteon.replace("__"," ");
		surveyName = form['survey'].value;
		survey = surveyName.replace("__"," ");
		user = form['user'].value;
		user1 = users.User(user);
		voter = users.get_current_user();
		surveyData = db.GqlQuery("SELECT * FROM Survey WHERE name =:1 and owner =:2",survey,user1);
		expireDate = "";
		for sur in surveyData:
			expireDate = sur.expiration;
		now = datetime.datetime.now();
		if (expireDate < now):
			return render_template('failure.html',message="This survey has expired. You can still view its result!");
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
	else:
		voteon = form['voteon'].value;
		vote = voteon.replace("__"," ");
		survey = form['survey'].value;
		surveyName = survey.replace("__"," ");
		user = form['user'].value;
		user1 = users.User(user);
		commenter = users.get_current_user();
		isCommented = db.GqlQuery("SELECT * FROM CommentValidator WHERE itemName = :1 AND itemOwner = :2 AND survey = :3 AND commenter = :4",vote,user1,surveyName,commenter);
		counter = isCommented.count();
		if(counter == 0):
				previousComment = db.GqlQuery("SELECT * FROM Comments WHERE itemName = :1 AND itemOwner = :2 AND survey = :3",vote,user1,surveyName);
				comment1 = "";
				for pre in previousComment:
					comment1 = pre.comment;
				newComment = comment1+str(commenter) + " said: "+form['commentText'].value + "; ";
				comment = Comments(itemName=vote,itemOwner=user1,survey=surveyName,comment=newComment);
				commentValidator = CommentValidator(itemName=vote,itemOwner=user1,survey=surveyName,commenter=commenter);
				comment.put();
				commentValidator.put();
				return render_template('failure.html',message="Comment successfully added!");
		else:
				return render_template('failure.html',message="You already have commented on this item!");




@app.route('/viewresults')
def viewResults():
	form = cgi.FieldStorage();
	surveyName = form['survey'].value;
	survey = surveyName.replace("__"," ");
        user = form['user'].value;
	owner = users.User(user);
	commenter = users.get_current_user();
	items = db.GqlQuery("SELECT * FROM Item WHERE survey = :1 and owner = :2",survey,owner);
	voteList = [];
	for item in items:
		winNumber = 0;
		win_count = db.GqlQuery("SELECT * FROM Vote WHERE name = :1 and survey = :2 and owner = :3",item.name,survey,owner);
		for win1 in win_count:
			winNumber = win1.win;
		comment = db.GqlQuery("SELECT * FROM Comments WHERE itemName = :1 AND itemOwner = :2 AND survey = :3",item.name,owner,survey);
		newComment="";
		for c in comment:
			newComment = c.comment;	
		resultString = item.name +"###" +str(winNumber) +"###"+newComment;
		voteList.append(resultString);
	return render_template('results.html',results=voteList);

@app.route('/addItems')
def addItems():
	form = cgi.FieldStorage();
        user = users.get_current_user();
        sName = form['addon'].value;
	sName1 = sName.split("__by__");
	sName2 = sName1[0]; 
	surveyName = sName2.replace("__"," ");
        rawOptions = form['additems'].value;
        rawOptions += ',';
        optionList = rawOptions.split(',');
        surveys = db.GqlQuery("SELECT * FROM Survey WHERE name = :1 and owner = :2",surveyName,user);
	oldItemList = [];
	for sur in surveys:
		if (sur.name == surveyName):
			oldItemList = sur.values;
	for newItems in optionList:
		oldItemList.append(newItems);
	newItemList = oldItemList;
	db.delete(surveys);
	newSurvey = Survey(name=surveyName,owner=user,values=newItemList);
	newSurvey.put();
	for option in optionList:
                        if option:
                                item = Item(name=option);
                                item.survey = surveyName;
                                item.owner = user;
                                search1 = Search(name=option,entityType="item",survey=surveyName,owner=user);
                                item.put();
                                search1.put();
	return render_template('survey_confirmation.html',survey=surveyName,option=optionList);

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
	oldSearch = db.GqlQuery("SELECT * FROM Search WHERE name = :1 and owner = :2 and survey = :3 and entityType = :4",item,owner,survey,"item");
	db.delete(oldSearch);
	return render_template('survey_confirmation.html',survey=survey,option=oldValues);

@app.route('/uploadfile',methods=['GET','POST'])
def uploadFile():
		form = cgi.FieldStorage();
		item = form["filename"];
		data = "";
		if item.file:
			data = item.file;
		doc = xml.dom.minidom.parse(data)
		items = doc.getElementsByTagName("NAME");
		owner = users.get_current_user();
		optionList = [];
		for node in items:
			optionList.append(node.firstChild.nodeValue);
		surveyName = optionList[0];
		optionList.remove(surveyName);
		newSurvey = Survey(name=surveyName,owner=owner,values=optionList);
		newSurvey.put();
		search = Search(name=surveyName,owner=owner,entotyType="Survey",survey=surveyName);
		search.put();
		for item in optionList:
			newItem = Item(name=item,survey=surveyName,owner=owner);
			search1 = Search(name=item,owner=owner,entotyType="item",survey=surveyName);
			newItem.put();
			search1.put();
		return render_template('survey_confirmation.html',survey=surveyName,option=optionList);
@app.route('/download')
def download():
	form = cgi.FieldStorage();
	rawOption = form['voteon'].value;
	optionList = rawOption.split("__by__");
	surveyName = optionList[0].replace("__"," ");
	user = users.User(optionList[1].strip());
	items = db.GqlQuery("SELECT * FROM Item WHERE owner = :1 and survey = :2",user,surveyName.strip());
	itemList = [];
	for item in items:
		itemList.append(item.name);
	def generate():
		textdata = "<CATEGORY>" + "\n" + "<NAME>" + surveyName +"</NAME>" + "\n";
		yield textdata;
		for i in itemList:
			text = "<ITEM>"+ "\n" + "<NAME>" + i + "</NAME>" + "\n" + "</ITEM>" + "\n";
			yield text;
		yield "</CATEGORY>";
	return Response(generate(), mimetype='text/csv');

@app.route('/search')
def search():
	form = cgi.FieldStorage();
	value = form['search'].value;
	searchValue = ".*" + value + ".*";
	searchString = db.GqlQuery("Select * from Search");
	searchList = [];
	for search in searchString:
		match = re.search(searchValue,search.name);
		if match:
			string = search.name + "###" + search.entityType + "###" + search.survey + "###" + str(search.owner);
			searchList.append(string);
	return render_template('searchresult.html',searchList=searchList);




