import os
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .models import Club, User
from werkzeug.utils import secure_filename
from . import db, ALLOWED_EXTENSIONS, UPLOAD_FOLDER

main = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def splitMemberString(members):
    return members.split(" ")

@main.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    club_list = db.session.query(Club).all()
    return render_template('index.html',club_list=club_list,user=current_user)

'''
Function to access club pages.

Using the clubID passed in the URL, use the club's member list to pull data from the 
User database, to then pass into a render_template function. You need a "members" variable and a "club" variable to pass into the function

I made a viewClub template so you can test if it works.
'''

@main.route("/club/<int:clubID>")
def viewClub(clubID):
    club = db.session.query(Club).filter(Club.id == clubID).first()
    memberList = splitMemberString(club.members) 
    users = db.session.query(User).all()
    UsersList = []
    for user in users:
        if str(user.id) in memberList:
            UsersList.append(user)
    return render_template('viewClub.html', club = club, members = UsersList)

@main.route("/join/<int:clubID>", methods=['GET','POST'])
def joinClub(clubID):
    club = db.session.query(Club).filter(Club.id == clubID).first()
    memberList = splitMemberString(club.members)
    # add line to redirect home if club doesn't exist
    if(club.members == ""):
        club.members = str(current_user.id)
    elif(str(current_user.id) in memberList):
        return redirect(url_for("main.index"))
    else:
        addtostring = " " + str(current_user.id)
        club.members += addtostring
    db.session.commit()
    return redirect(url_for("main.index"))

'''
Function for leaving clubs.
Uses similar logic to joining clubs.

I made a splitMemberString helper function at the top of this file.
'''
@main.route("/leave/<int:clubID>", methods=['GET','POST'])
def leaveClub(clubID):
    club = db.session.query(Club).filter(Club.id == clubID).first()
    user_to_leave = current_user.id
    memberList = splitMemberString(club.members)
    if(str(user_to_leave) in memberList):
        memberList.remove(str(user_to_leave))
        newList = " ".join(memberList)
        club.members = newList
    else:
        return redirect(url_for("main.index"))
    db.session.commit()
    return redirect(url_for("main.index"))


@main.get("/NewClub")
def create():
    return render_template("newClub.html")

@main.post("/add")
def add():
    cname = request.form.get("clubname")
    ctype = request.form.get("clubtype")
    cimage = request.files['clubPic']
    if(cimage.filename == ""):
        newClub = Club(name=cname,type=ctype,members="",pictureName="orange.png")
    else:
        filename = secure_filename(cimage.filename)
        cimage.save(os.path.join(UPLOAD_FOLDER, filename))
        newClub = Club(name=cname,type=ctype,members="",pictureName=filename)
    db.session.add(newClub)
    db.session.commit()
    return redirect(url_for("main.index"))

@main.route("/add_image/<int:clubID>", methods=['GET','POST'])
def add_image(clubID):
    club = db.session.query(Club).filter(Club.id == clubID).first()
    cimage = request.files['clubPic']
    if(cimage.filename == ""):
        return redirect(url_for("main.viewClub", clubID=clubID))
    else:
        filename = secure_filename(cimage.filename)
        cimage.save(os.path.join(UPLOAD_FOLDER, filename))
        club.pictureName = filename
    db.session.commit()
    return redirect(url_for("main.viewClub", clubID=clubID))
    

@main.get("/delete/<int:clubID>")
def delete(clubID):
    club = db.session.query(Club).filter(Club.id == clubID).first()
    path = os.path.join(UPLOAD_FOLDER,club.pictureName)
    os.remove(path)
    db.session.delete(club)
    db.session.commit()
    return redirect(url_for("main.index"))

