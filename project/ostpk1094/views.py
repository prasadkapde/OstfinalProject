from ostpk1094 import app
from ostpk1094.models import Survey
from random import randint
from ostpk1094.models import Item
from ostpk1094.models import Vote, Comments, CommentValidator, Search
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
	if (form['startup'].value == "allresults"):
		items = db.GqlQuery("SELECT * FROM Vote");
		listOfresults=[];
		for item in items:
			comment = db.GqlQuery("SELECT * FROM Comments WHERE itemName = :1 AND itemOwner = :2 AND survey = :3",item.name,item.owner,item.survey);
			newComment = "";
			for c in comment:
				newComment = c.comment;
			newString = item.name+"###"+item.survey+"###"+str(item.owner)+"###"+str(item.win)+"###"+newComment;
			listOfresults.append(newString);
		return render_template('allresults.html',results=listOfresults);
	if (form['startup'].value == "create"):
		return render_template('survey.html');
	if (form['startup'].value == "listmysurvey"):
                user = users.get_current_user();
	        surveys = db.GqlQuery("SELECT * FROM Survey WHERE owner = :1",user);
		listOfSurveys = [];
		for sur in surveys:
			name1 = sur.name+" by " + str(user);
			listOfSurveys.append(name1);
		if (len(listOfSurveys) > 0):
			return render_template('listsurveys.html',surveys=listOfSurveys,for_user=user,path="vote");
		else:
			return render_template('failure.html',message="You don't have any categories to list. Create Category first.");
	if (form['startup'].value == "listallsurvey" or form['startup'].value == "download"):
                user = users.get_current_user();
                surveys = db.GqlQuery("SELECT * FROM Survey");
                listOfSurveys = [];
                for sur in surveys:
                	val = sur.name+" by " + str(sur.owner);
                	listOfSurveys.append(val);
                if (len(listOfSurveys) > 0):
                	if (form['startup'].value == "listallsurvey"):
	                		return render_template('listsurveys.html',surveys=listOfSurveys,for_user="All Users",path="vote");
	            	else:
	                		return render_template('listsurveys.html',surveys=listOfSurveys,for_user="All Users",path="download");
                else:
                	return render_template('failure.html',message="No surveys to list.");

	if (form['startup'].value == "rename"):
		user = users.get_current_user();
		surveys = db.GqlQuery("SELECT * FROM Survey WHERE owner = :1",user);
		counter = surveys.count();
		if (counter > 0):
			listOfSurveys = [];
			for sur in surveys:
				listOfSurveys.append(sur.name);
			return render_template('renamecategory.html',surveys = listOfSurveys);
		else:
			return render_template('failure.html',message="You don't have any categories to rename. Create Category first.");

	if (form['startup'].value == "delete"):
		user = users.get_current_user();
		surveys = db.GqlQuery("SELECT * FROM Survey WHERE owner = :1",user);
		counter = surveys.count();
		if (counter > 0):
			listOfSurveys = [];
			for sur in surveys:
				listOfSurveys.append(sur.name);
			return render_template('deletecategory.html',surveys = listOfSurveys);
		else:
			return render_template('failure.html',message="You don't have any categories to delete. Create Category first.");

	if (form['startup'].value == "addItems"):
		user = users.get_current_user();
		surveys = db.GqlQuery("SELECT * FROM Survey WHERE owner = :1",user);
		listOfSurveys = [];
		for sur in surveys:
			name1 = sur.name+" by " + str(user);
			listOfSurveys.append(name1);
		if(len(listOfSurveys) > 0):
			return render_template('listsurveys.html',surveys=listOfSurveys,for_user=str(user),path="add");
		else:
			return render_template('failure.html',message="You don't have any categories to add items. Create Category first.");

	if (form['startup'].value == "delItems"):
                user = users.get_current_user();
                surveys = db.GqlQuery("SELECT * FROM Survey WHERE owner = :1",user);
                listOfSurveys = [];
                for sur in surveys:
                        name1 = sur.name+" by " + str(user);
                        listOfSurveys.append(name1);
                if(len(listOfSurveys) > 0):
                	return render_template('listsurveys.html',surveys=listOfSurveys,for_user=str(user),path="delete");
                else:
                	return render_template('failure.html',message="You don't have any categories to delete items. Create Category first.");
	if (form['startup'].value == "upload"):			
		return render_template('upload.html');

	if (form['startup'].value == "reset"):		
		user = users.get_current_user();
		surveys = db.GqlQuery("SELECT * FROM Survey WHERE owner = :1",user);
		counter = surveys.count();
		if (counter > 0):
			listOfSurveys = [];
			for sur in surveys:
				listOfSurveys.append(sur.name);
			return render_template('reset.html',surveys = listOfSurveys);
		else:
			return render_template('failure.html',message="You don't have any categories to reset. Create Category first.");

@app.route('/updateExpiration')
def updateExpiration():
	form = cgi.FieldStorage();
	user = users.get_current_user();
	oldSurveyName = form['update'].value;
	surveyExpireDate = "";
	if (form.has_key("dateValue")):
		expireDate = form['dateValue'].value;
		expireHour = int(form['hours'].value);
		expireMinutes = int(form['minutes'].value);
		expireSeconds = int(form['seconds'].value);
		rawDate = expireDate.split("/");
		month = int(rawDate[0]);
		day = int(rawDate[1]);
		year = int(rawDate[2]);
		surveyExpireDate = datetime.datetime(year,month,day,expireHour,expireMinutes,expireSeconds);
	else:
		surveyExpireDate = datetime.datetime(2012,12,30,0,0,0);
	oldSurvey = db.GqlQuery("SELECT * FROM Survey WHERE name = :1 AND owner = :2",oldSurveyName,user);
	newSurvey="";
	for old in oldSurvey:
		newSurvey= Survey(name=old.name,values=old.values,owner=old.owner,expiration=surveyExpireDate);
	db.delete(oldSurvey);
	newSurvey.put();
	return render_template('failure.html',message="Update Successful.");

@app.route('/addsurvey')
def addSurvey():
	form = cgi.FieldStorage();
	user = users.get_current_user();
	surveyName = form['sname'].value.strip();	
	rawOptions = form['options'].value;
	rawOptions += ',';
	optionList = rawOptions.split(',');
	surveyExpireDate = "";
	if (form.has_key("dateValue")):
		expireDate = form['dateValue'].value;
		expireHour = int(form['hours'].value);
		expireMinutes = int(form['minutes'].value);
		expireSeconds = int(form['seconds'].value);
		rawDate = expireDate.split("/");
		month = int(rawDate[0]);
		day = int(rawDate[1]);
		year = int(rawDate[2]);
		surveyExpireDate = datetime.datetime(year,month,day,expireHour,expireMinutes,expireSeconds);
	else:
		surveyExpireDate = datetime.datetime(2012,12,30,0,0,0);
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
		
def deleteGeneric(surveyName):
	user = users.get_current_user();
	surveys = db.GqlQuery("SELECT * FROM Survey WHERE owner = :1 AND name = :2",user,surveyName);
	db.delete(surveys);
	items = db.GqlQuery("SELECT * FROM Item WHERE survey = :1 and owner = :2",surveyName,user);
	db.delete(items);
	votes = db.GqlQuery("SELECT * FROM Vote WHERE survey = :1 and owner = :2",surveyName,user);
	db.delete(votes);
	search = db.GqlQuery("SELECT * FROM  Search WHERE survey = :1 AND owner = :2",surveyName,user);
	db.delete(search);
	comments = db.GqlQuery("SELECT * FROM Comments WHERE itemOwner = :1 AND survey = :2",user,surveyName);
	db.delete(comments);
	commentValidator = db.GqlQuery("SELECT * FROM CommentValidator where itemOwner = :1 and survey = :2",user,surveyName);
	db.delete(commentValidator);

@app.route('/deleteCategory')
def deleteCategory():
	form = cgi.FieldStorage();
	surveyName = form['deletesurvey'].value;	
	deleteGeneric(surveyName=surveyName);
	return render_template('failure.html',message="Record Deleted!");

@app.route('/renameCategory')
def renameCategory():
	form = cgi.FieldStorage();
	user = users.get_current_user();
	newSurveyName = form['renameText'].value.strip();
	oldSurveyName = form['renamesurvey'].value;
	newNameCheck = db.GqlQuery("SELECT * FROM Survey WHERE owner = :1 AND name = :2",user,newSurveyName);
	counter = newNameCheck.count();
	if (counter > 0):
			return render_template('failure.html',message="You already have a survey with given name. Please try with some other name");
	else:
		oldSurvey = db.GqlQuery("SELECT * FROM Survey WHERE owner = :1 AND name = :2",user,oldSurveyName);
		for old in oldSurvey:
			newSurvey = Survey(name=newSurveyName,values=old.values,owner=old.owner,expiration=old.expiration);
			newSurvey.put();
		oldItems = db.GqlQuery("SELECT * FROM Item WHERE survey = :1 and owner = :2",oldSurveyName,user);
		for old in oldItems:
			newItem = Item(name=old.name,image=old.image,survey=newSurveyName,owner=old.owner);
			newItem.put();
		oldVotes = db.GqlQuery("SELECT * FROM Vote WHERE survey = :1 and owner = :2",oldSurveyName,user);
		for old in oldVotes:
			newVote = Vote(name=old.name,owner=old.owner,win=old.win,survey=newSurveyName);
			newVote.put();
		oldComments = db.GqlQuery("SELECT * FROM Comments WHERE itemOwner = :1 AND survey = :2",user,oldSurveyName);
		for old in oldComments:
			newComment = Comments(itemName=old.itemName,itemOwner=old.itemOwner,comment=old.comment,survey=newSurveyName);
			newComment.put();
		oldCommentValidator = db.GqlQuery("SELECT * FROM CommentValidator where itemOwner = :1 and survey = :2",user,oldSurveyName);
		for old in oldCommentValidator:
			newCommentValidator = CommentValidator(itemName=old.itemName,itemOwner=old.itemOwner,commenter=old.commenter,survey=newSurveyName);
			newCommentValidator.put();
		oldSearch = db.GqlQuery("SELECT * FROM  Search WHERE survey = :1 AND owner = :2",oldSurveyName,user);
		for old in oldSearch:
			if(old.entityType == "survey"):
				newSearch = Search(name=newSurveyName,entityType=old.entityType,survey=newSurveyName,owner=old.owner);
				newSearch.put();
			else:
				newSearch = Search(name=old.name,entityType=old.entityType,survey=newSurveyName,owner=old.owner);
				newSearch.put();
		deleteGeneric(surveyName=oldSurveyName);
		return render_template('failure.html',message="Update Successful!");

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
	optionList = rawOption.split(" by ");
	surveyName = optionList[0].replace("__"," ");
	tempUser = optionList[1].strip();
	if not "@" in tempUser:
		tempUser = tempUser + "@gmail.com";
	user = users.User(tempUser);
	itemList = db.GqlQuery("SELECT * FROM Item WHERE survey = :1 and owner = :2",surveyName,user);
	options = [];
	for i in itemList:
		options.append(i.name);
	if (path == "vote") and (len(options) < 2):
		return render_template('failure.html',message="This category has less than two options, voting not allowed on this.");
	if (path == "vote") and (len(options) >= 2):
		length = len(options) - 1;
		one = randint(0,length);
		two = randint(0,length);
		while (one == two):
			two = randint(0,length);
		newList = [];
		newList.append(options[one]);
		newList.append(options[two]);
		return render_template('voting.html',surveys=surveyName,user=user,options=newList,path=path);	
	if (path == "delete"):
		return render_template('voting.html',surveys=surveyName,user=user,options=options,path=path);

@app.route('/registervote')
def registerVote():
	form = cgi.FieldStorage();
	if(form.has_key('vote')):
		voteon = form['voteon'].value;
		vote = voteon.replace("__"," ");
		surveyName = form['survey'].value;
		survey = surveyName.replace("__"," ");
		user = form['user'].value.strip();
		tempUser = user;
		if not "@" in tempUser:
			tempUser = tempUser + "@gmail.com";
		user1 = users.User(tempUser);
		voter = users.get_current_user();
		surveyData = db.GqlQuery("SELECT * FROM Survey WHERE name =:1 and owner =:2",survey,user1);
		expireDate="";
		for sur in surveyData:
			expireDate = sur.expiration;
		if (expireDate < datetime.datetime.now()):
			return render_template('failure.html',message="This survey has expired. You can still view its result!");
		winnerVote = db.GqlQuery("SELECT * FROM Vote WHERE owner = :1 and survey = :2 and name = :3",user1,survey,vote);
		win_number = 1;
		for i in winnerVote:
				win_number = i.win;
				win_number += 1;
		db.delete(winnerVote);
		newVote = Vote(name=vote,survey=survey,owner=user1,win=win_number);
		newVote.put();
		return render_template('successful_voting.html',winner=vote,looser=" All Others.");
		
	else:
		voteon = form['voteon'].value;
		vote = voteon.replace("__"," ");
		survey = form['survey'].value;
		surveyName = survey.replace("__"," ");
		user = form['user'].value.strip();
		tempUser = user;
		if not "@" in tempUser:
			tempUser = tempUser + "@gmail.com";
		user1 = users.User(tempUser);
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
				db.delete(previousComment);
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
	user = form['user'].value.strip();
	tempUser = user;
	if not "@" in tempUser:
		tempUser = tempUser + "@gmail.com";
	owner = users.User(tempUser);
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
	sName1 = sName.split(" by ");
	sName2 = sName1[0]; 
	surveyName = sName2.replace("__"," ");
	rawOptions = form['additems'].value;
	rawOptions += ',';
	optionList = rawOptions.split(',');
	counter = 0;
	for option in optionList:
			itemPresent = db.GqlQuery("SELECT * FROM Item WHERE name = :1 AND survey = :2 and owner = :3",option,surveyName,user);
			counter1 = itemPresent.count();
			if (counter1 > 0):
				counter = counter + 1;
	if (counter > 0):
		return render_template('failure.html',message="One or more items that you tried to add are already present in this category.None of the items were added.");
	else:
		surveys = db.GqlQuery("SELECT * FROM Survey WHERE name = :1 and owner = :2",surveyName,user);
		oldItemList = [];
		oldExpiration ="";
		for sur in surveys:
			if (sur.name == surveyName):
				oldItemList = sur.values;
				oldExpiration = sur.expiration;
		for newItems in optionList:
			oldItemList.append(newItems);
		newItemList = oldItemList;
		db.delete(surveys);
		newSurvey = Survey(name=surveyName,owner=user,values=newItemList,expiration=oldExpiration);
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
	oldExpiration="";
	for sur in oldSurvey:
		oldValues = sur.values;
		oldExpiration = sur.expiration;
	oldValues.remove(item);
	newSurvey = Survey(name=survey,owner=owner,values=oldValues,expiration=oldExpiration);
	db.delete(oldSurvey);
	newSurvey.put();
	oldItem = db.GqlQuery("SELECT * FROM Item WHERE name = :1 and owner = :2 and survey = :3",item,owner,survey);
	db.delete(oldItem);
	oldSearch = db.GqlQuery("SELECT * FROM Search WHERE name = :1 and owner = :2 and survey = :3 and entityType = :4",item,owner,survey,"item");
	db.delete(oldSearch);
	oldComment = db.GqlQuery("SELECT * FROM Comments WHERE itemName = :1 AND itemOwner = :2 AND survey = :3",item,owner,survey);
	db.delete(oldComment);
	oldCommentValidator = db.GqlQuery("SELECT * FROM CommentValidator WHERE itemName = :1 AND itemOwner = :2 AND survey = :3",item,owner,survey);
	db.delete(oldCommentValidator);
	oldVote = db.GqlQuery("SELECT * FROM Vote WHERE name = :1 AND owner = :2 AND survey = :3",item,owner,survey);
	db.delete(oldVote);
	return render_template('failure.html',message="Item Deleted Sucessfully!");

@app.route('/uploadfile',methods=['GET','POST'])
def uploadFile():
	try:
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
		surveyName = optionList[0].strip();
		optionList.remove(surveyName);		
		surveyCheck = db.GqlQuery("SELECT * FROM Survey WHERE name = :1 and owner = :2",surveyName,owner);
		surveyCount = surveyCheck.count();
		if (surveyCount > 0):
			##Get the old item list from Survey.
			oldList = [];
			oldExpiration = "";
			for sur in surveyCheck:
				oldList = oldList+sur.values;
				oldExpiration = sur.expiration;
			addList = []; ## Items that are present in both list;
			removeList = [] ## Items to be deleted.
			listCounter = 0;
			tempList = optionList;
			for old in oldList:
				if(old in optionList):
					addList.append(old);
					optionList.remove(old);
					listCounter = listCounter + 1;
				else:
					removeList.append(old);
			if (len(addList) == len(tempList)) and (listCounter == len(tempList))and (len(removeList) == 0):
				removeList = tempList;
			for remove in removeList:
				oldItem = db.GqlQuery("SELECT * FROM Item WHERE name = :1 and owner = :2 and survey = :3",remove,owner,surveyName);
				db.delete(oldItem);
				oldSearch = db.GqlQuery("SELECT * FROM Search WHERE name = :1 and owner = :2 and survey = :3 and entityType = :4",remove,owner,surveyName,"item");
				db.delete(oldSearch);
				oldComment = db.GqlQuery("SELECT * FROM Comments WHERE itemName = :1 AND itemOwner = :2 AND survey = :3",remove,owner,surveyName);
				db.delete(oldComment);
				oldCommentValidator = db.GqlQuery("SELECT * FROM CommentValidator WHERE itemName = :1 AND itemOwner = :2 AND survey = :3",remove,owner,surveyName);
				db.delete(oldCommentValidator);
				oldVote = db.GqlQuery("SELECT * FROM Vote WHERE name = :1 AND owner = :2 AND survey = :3",remove,owner,surveyName);
				db.delete(oldVote);
			for item in optionList:
				newItem = Item(name=item,survey=surveyName,owner=owner);
				search1 = Search(name=item,owner=owner,entityType="item",survey=surveyName);
				newItem.put();
				search1.put();
			for add in addList:
				optionList.append(add);
			db.delete(surveyCheck);
			newSurvey = Survey(name=surveyName,owner=owner,values=optionList,expiration=oldExpiration);
			newSurvey.put();
		else:
			surveyExpireDate = datetime.datetime(2012,12,30,00,00,00);
			newSurvey = Survey(name=surveyName,owner=owner,values=optionList,expiration=surveyExpireDate);
			newSurvey.put();
			search = Search(name=surveyName,owner=owner,entityType="Survey",survey=surveyName);
			search.put();
			for item in optionList:
				newItem = Item(name=item,survey=surveyName,owner=owner);
				search1 = Search(name=item,owner=owner,entityType="item",survey=surveyName);
				newItem.put();
				search1.put();
		return render_template('survey_confirmation.html',survey=surveyName,option=optionList);
	except:
		return render_template('failure.html',message="The file you uploaded was incorrect!");


@app.route('/download')
def download():
	form = cgi.FieldStorage();
	rawOption = form['voteon'].value;
	optionList = rawOption.split(" by ");
	surveyName = optionList[0].replace("__"," ");
	tempUser = optionList[1].strip();
	if not "@" in tempUser:
		tempUser = tempUser + "@gmail.com";
	user = users.User(tempUser);
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