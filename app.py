from flask import Flask, redirect, url_for, render_template, request, session, flash, get_flashed_messages
from datetime import timedelta
import boto3
from boto3.session import Session
import key_config
from boto3.dynamodb.conditions import Key, Attr
from forms import queryForm


app = Flask(__name__)



dynamo_resource = boto3.resource('dynamodb', region_name='us-east-1', aws_access_key_id = key_config.ACCESS_KEY_ID, aws_secret_access_key = key_config.ACCESS_SECRET_KEY)

s3c = boto3.client('s3', region_name='us-east-1', aws_access_key_id = key_config.ACCESS_KEY_ID, aws_secret_access_key = key_config.ACCESS_SECRET_KEY)

dynamo_client = boto3.client('dynamodb', region_name='us-east-1', aws_access_key_id=key_config.ACCESS_KEY_ID, aws_secret_access_key=key_config.ACCESS_SECRET_KEY)


# #all of the sesion data is encrypted on teh server
# #you need a secret key the program can use to unencrypt
app.secret_key = "qwet12568"
app.permanent_session_lifetime = timedelta(days=1) #how long your permanent session data

bucket_name = 'assignmentoneflaskimagebucket'
music_table = dynamo_resource.Table('music')
sub_table = dynamo_resource.Table('subscription')




@app.route("/landing", methods=['GET','POST'])
def home():
    # user section
    user_name = session['user']

#     #subscription area

    response = sub_table.query(KeyConditionExpression=Key('userid').eq(user_name))
    items = response['Items']
    music_list = [item['track'] for item in items]
    keys_to_get = [{'title': {'S' : title}} for title in music_list]

    table_name = 'music'
    if keys_to_get:
        response = dynamo_client.batch_get_item(
            RequestItems={
                'music': {
                'Keys': keys_to_get,
                }
            }
        )
        items = response.get('Responses', {}).get(table_name, [])
    else:
        items = []

    music=[]
    for item in items:
        music_item={}
        music_item['title'] = item.get('title', {}).get('S')
        music_item['artist'] = item.get('artist', {}).get('S')
        music_item['year'] = item.get('year', {}).get('S')
        music_item['img_url'] = item.get('img_url', {}).get('S')
        music_item['web_url'] = item.get('web_url', {}).get('S')
        music.append(music_item)

  


    for track in music:
        image_key = track['title'] + '.jpg'
        image_url = s3c.generate_presigned_url(ClientMethod='get_object', Params={'Bucket':bucket_name, 'Key': image_key})
        track['s3_image'] = image_url


    return render_template("landing.html", music=music, user=user_name)



@app.route("/all_music", methods=['GET',"POST"])
def all_music():
    response = music_table.scan()
    music = response['Items']

    for track in music:
        image_key = track['title'] + '.jpg'
        image_url = s3c.generate_presigned_url(ClientMethod='get_object', Params={'Bucket':bucket_name, 'Key': image_key})
        track['s3_image'] = image_url

    while 'LastEvaluatedKey' in response:
        response=music_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        music.extend(response['Items'])
    
    return render_template("all_music.html", music=music)


@app.context_processor
def base():
    form = queryForm()
    logo = get_logo()
    return dict(form=form, logo_url=logo)

def get_logo():
    object_key = 'logo.png'
    url = s3c.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': object_key})
    return url

# #Create search function
@app.route('/search', methods=["POST"]) # type: ignore
def search():
    form = queryForm()
    title_searched = form.searched_title.data
    artist_searched = form.searched_artist.data
    year_searched = form.searched_year.data
    table = dynamo_resource.Table('music')
    
    if not(title_searched) and not artist_searched and not year_searched:
        return render_template("search.html", searched1=artist_searched, searched2=title_searched)

    if title_searched:
        response_title = table.query(KeyConditionExpression=Key('title').eq(title_searched))
        items = response_title['Items']
        if artist_searched:
            items = list(filter(lambda x: x['artist'] == artist_searched, items))
            if year_searched:
                items = list(filter(lambda x: x['year'] == year_searched, items))
        elif year_searched:
            items = list(filter(lambda x:x['year'] == year_searched, items))
    elif artist_searched:
        response = table.scan(FilterExpression=Attr('artist').eq(artist_searched))
        items = response['Items']
        if year_searched:
            items = list(filter(lambda x: x['year'] == year_searched, items))
    else:
        response = table.scan(FilterExpression=Attr('year').eq(year_searched))
        items = response['Items']
        if artist_searched:
            items = list(filter(lambda x: x['artist'] == artist_searched, items))
        elif year_searched:
            items = list(filter(lambda x:x['year'] == year_searched, items))
        else:
            items = []


    for item in items:
        image_key = item['title'] + '.jpg'
        image_url = s3c.generate_presigned_url(ClientMethod='get_object', Params={'Bucket':bucket_name, 'Key': image_key})
        item['s3_image'] = image_url

    if items:
        return render_template("search.html", searched2=artist_searched, searched1=title_searched, searched3=year_searched, result=items)
    else:
        flash('No result is retrieved. Please query again')
        return redirect(url_for("home"))

@app.route('/subscribe')
def subscribe():
    track_title = request.args.get('track_id')
    user = session['user']

    sub_table.put_item(
                Item={
                'userid':user,
                'track':track_title,
                }
            )
    
    flash("You are now subscribed!")
    return redirect(url_for('home'))



@app.route("/", methods=["POST", "GET"])
def login():
        return render_template("login.html")
    
@app.route("/check", methods=["POST"])
def check():
    if request.method=='POST':
        session.permanent = True

        email = request.form['email']
        password = request.form['password']

        table = dynamo_resource.Table('login')
        response = table.query(
                KeyConditionExpression=Key('email').eq(email)
        )
        items = response['Items']
        try:
            user_name = items[0]['user_name']
            session['user'] = user_name
            if password == items[0]['password']:
                session['logged_in'] = True
                return redirect( url_for('home'))
            else:
                raise ValueError
        except:
            flash("email or password is invalid", "info")
            return redirect(url_for('login'))
        


@app.route("/logout")
def logout():
    flash("You have been logged out", "info")
    session.pop("user", None) #removes user data from session
    session.pop("email", None)
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/signup", methods=["POST","GET"])
def signup():
    if request.method=="POST":
        email = request.form['email']
        user_name = request.form['user_name']
        password = request.form['password']

        if not email or not user_name or not password:
            flash("Please fill out all of the fields","error")
            return render_template('signup.html', messages=get_flashed_messages())

        table = dynamo_resource.Table('login')
        response = table.query(
                KeyConditionExpression=Key('email').eq(email)
        )
        items = response['Items']
        if len(items):
            flash("The email already exists", "info")
            return render_template('signup.html', messages=get_flashed_messages())
        else:
            table.put_item(
                Item={
                'email':email,
                'user_name':user_name,
                'password':password
                }
            )

        flash("Registration Complete. Please login to your account")

        return render_template('login.html')
    return render_template('signup.html')

@app.route("/delete/<string:title>", methods=['GET'])
def delete(title):
    table = dynamo_resource.Table('subscription')
    user_name = session['user']
    response = table.get_item(Key = {'userid':user_name,'track':title})
    if 'Item' not in response:
        flash("Unable to find track: {}".format(title), "info")
        return redirect(url_for('home'))
    
    response = table.delete_item(Key = {'userid':user_name,'track':title})
    if response:
        flash('Subscription successfully deleted')
    return redirect(url_for('home'))
    
    

    

if __name__ == "__main__":
    app.run(debug=True)