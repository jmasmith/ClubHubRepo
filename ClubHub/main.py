import os
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from ClubHub.models import Club, User
from werkzeug.utils import secure_filename
from ClubHub.__init__ import db, ALLOWED_EXTENSIONS, UPLOAD_FOLDER

main = Blueprint('main', __name__)

'''
allowed_file

Returns true if filename contains a period AND if
file is of an image type (jpg, jpeg, png, gif)
'''
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

'''
splitMemberString

Helper function to easily return the member string for
each club as an array of numbers (still in string form)
'''
def splitMemberString(members):
    return members.split(" ")

'''
Route for Homepage

Queries Club DB for all existing clubs to populate home page
'''
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
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    club = db.session.query(Club).filter(Club.id == clubID).first()
    # prevents url bar abuse
    if not club:
        return redirect(url_for("main.index"))
    memberList = splitMemberString(club.members) 
    users = db.session.query(User).all()
    UsersList = []
    for user in users:
        if str(user.id) in memberList:
            UsersList.append(user)
    return render_template('viewClub.html', club = club, members = UsersList)

'''
Join Club

After assuring the club exists in database,
and that current_user isn't already in the club,
adds current_user ID to member list
'''
@main.route("/join/<int:clubID>", methods=['GET','POST'])
def joinClub(clubID):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    club = db.session.query(Club).filter(Club.id == clubID).first()
    # prevents url bar abuse
    if not club:
        return redirect(url_for("main.index"))
    memberList = splitMemberString(club.members)
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
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    club = db.session.query(Club).filter(Club.id == clubID).first()
    # prevents url bar abuse
    if not club:
        return redirect(url_for("main.index"))
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

'''
New Club

Renders HTML form for creating new club
'''
@main.get("/NewClub")
def create():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template("newClub.html")

'''
Add Club

Pulls data from newclub form to actually create the new club
'''
@main.post("/add")
def add():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    cname = request.form.get("clubname")
    ctype = request.form.get("clubtype")
    cimage = request.files['clubPic']
    if(cimage.filename == "" or not allowed_file(cimage.filename)):
        newClub = Club(name=cname,type=ctype,members="",pictureName="orange.png")
    else:
        filename = secure_filename(cimage.filename)
        cimage.save(os.path.join(UPLOAD_FOLDER, filename))
        newClub = Club(name=cname,type=ctype,members="",pictureName=filename)
    db.session.add(newClub)
    db.session.commit()
    return redirect(url_for("main.index"))

'''
Add Image

Using the modal popup in the view club page, allows user to
upload an image file to static folder and add that image's 
name to the club's pictureName field
'''
@main.route("/add_image/<int:clubID>", methods=['GET','POST'])
def add_image(clubID):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    club = db.session.query(Club).filter(Club.id == clubID).first()
    # prevents url bar abuse
    if not club:
        return redirect(url_for("main.index"))
    cimage = request.files['clubPic']
    if(cimage.filename == "" or not allowed_file(cimage.filename)):
        return redirect(url_for("main.viewClub", clubID=clubID))
    else:
        filename = secure_filename(cimage.filename)
        cimage.save(os.path.join(UPLOAD_FOLDER, filename))
        club.pictureName = filename
    db.session.commit()
    return redirect(url_for("main.viewClub", clubID=clubID))
    
'''
Delete Club

After ensuring the club exists and that it's not using the default image
for it's picture, deletes both the club and its image in the static folder.

If it's using the default image, it just deletes the club from the club
database.
'''
@main.get("/delete/<int:clubID>")
def delete(clubID):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    club = db.session.query(Club).filter(Club.id == clubID).first()
    # Deletes image if not default image
    if(club.pictureName != "orange.png"):
        path = os.path.join(UPLOAD_FOLDER,club.pictureName)
        os.remove(path)
    db.session.delete(club)
    db.session.commit()
    return redirect(url_for("main.index"))

