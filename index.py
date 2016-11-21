#! /usr/bin/python

## GLOBAL IMPORTS
from imports import *

## LOCAL IMPORTS
from functions import *


## CONGFIURATION

logging.basicConfig(level = logging.DEBUG)
app = Flask(__name__)
app.config.from_pyfile('config.cfg')


##SETUP
@app.before_request
def sessionhandling():
    g.con = connect()


##END POINTS
@app.route('/', methods = ['GET', 'POST'])
def test():
    images = []
    qry = '''SELECT CASE WHEN parent_image IS NULL THEN id ELSE parent_image END AS id, image_width as width, thumb_type, image_height as height FROM image WHERE image_size = 3 AND visible = TRUE ORDER BY random()'''
    cur = query( qry )
    for row in cur.fetchall():
        image = {}
        image['src'] = '/image/'+str(row[0])+'_'+str(row['thumb_type'])+'_t'
        image['width'] = row[1]
        image['type'] = row[2]
        image['height'] = row[3]
        image['large_src'] = '/image/'+str(row[0])
        image['title'] = '&copy; Callum Trayner 2015'
        images.append(image)
    images = images + images
    shuffle(images)
    return render_template('layout.html', images = images)


@app.route('/tmp/image/<imagename>', methods = ['GET', 'POST'])
def get_temp( imagename ):
    if '..' in imagename or imagename.startswith('/'):
        abort(404)
    return send_from_directory( app.config['TEMP_FOLDER'], imagename, as_attachment = False, mimetype = 'image/jpeg' )


@app.route('/background/', methods = [ 'GET', 'POST'] )
def background():
	return send_from_directory( '.', 'background.jpg', as_attachment = False, mimetype = 'image/jpeg' )


@app.route('/image/<id>', methods = ['GET', 'POST'])
def image(id):
	#FIXME: should be serving from disk rather than the database.
	return serve_from_disk( id )

@app.route('/upload/', methods = ['GET', 'POST'])
def upload():
    file = None
    im = None
    if 'tmpfile' in request.files:
        file = request.files['tmpfile']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
	try:
	    im = Image.open(file.stream)
	    output_name = app.config['TEMP_FOLDER']+filename[:filename.rfind('.')]+'.tmp'
            gen_location()
	    im.save( output_name, 'JPEG' )
	except Exception, e:
            logging.exception('Probably not an image?')
            print e #probably not an image. Should have something on the javascript to make sure we're only uploading images.

    if im:
        data = {}
        data['x'] = im.size[0]
        data['y'] = im.size[1]
        data['format'] = im.format
        data['aspect_ratio'] = im.size[0] / im.size[1]
        data['url'] = url_for( 'get_temp', imagename = filename[:filename.rfind('.')]+'.tmp' )
        return json( data = data, message = 'Uploaded successfully' ) 
    else:
	return Response('<html><h1>Upload Failed. See Log</h1></html>', mimetype= 'text/html')


@app.route('/saveconfiguration/', methods = ['GET', 'POST'])
def save_configuration():
    filename = None
    if 'url' in request.form:
        filename = request.form['url']
    elif 'url' in request.args:
        filename = request.args['url']
    if filename:
        filename = filename[filename.rfind('/')+1:] #strips out the /tmp/image

    if not filename:
        return json( message = 'No URL given.', error = True )

    im = Image.open( app.config['TEMP_FOLDER']+filename )
    filename = filename[:filename.rfind('.')]
    f = StringIO.StringIO()
    im.save(f, 'JPEG')

    parent_id = None
    q = '''SELECT id, max_height, appendix FROM image_size ORDER BY id DESC;'''
    cur = query ( q )
    cur2 = None
    #qry = '''INSERT INTO image (image_name, author_id, image_width, image_height, thumb_type, image, image_size, gallery_id, parent_image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;'''
    for t in cur.fetchall():
        img_scale = im.copy()
        width = None
        height = None
        if t['max_height'] is not None:
            width = float( t['max_height'] * ( im.size[0] / im.size[1] ) ) 
            height = t['max_height']
            img_scale.thumbnail( ( width, height ), Image.ANTIALIAS )
        else:
            width = im.size[0]
            height = im.size[1]

        f = StringIO.StringIO()
        img_scale.save(f, 'JPEG')

        #args = ( filename, 1, width, height, 1, psycopg2.Binary( f.getvalue() ), t['id'], 1, parent_id )
        #cur2 = query( qry, args, cursor = cur2 )
        #logging.debug( 'Inserted: %d' % ( cur2.rowcount ) )
        #if t['max_height'] is None:
        #    parent_id = cur2.fetchone()[0]
        res = write_to_disk( f, filename, height, width, t['id'], 1, parent_id, 1, 1 )
	if t['max_height'] is None:
		parent_id = res	
        f.close()

    q = '''SELECT id, max_height, appendix FROM image_size WHERE max_height IS NOT NULL ORDER BY id DESC;'''

    #then we need to write our thumbnail.
    cur = query( q, cursor = cur )
    for t in cur.fetchall():
        f = StringIO.StringIO()
        thumb = im.copy()

        thumb_box = ( int(float(request.form['thumb_x'])), int(float(request.form['thumb_y'])), int(float(request.form['thumb_x']) + float(request.form['thumb_width'])), int(float(request.form['thumb_y']) + float(request.form['thumb_height'])) )
        thumb = thumb.crop( thumb_box )

        width = int(t['max_height']) * float(request.form['thumb_aspect'])
        height = int(t['max_height'])

        thumb.thumbnail( (width, height), Image.ANTIALIAS )
        f = StringIO.StringIO()
        thumb.save( f, 'JPEG' )

        #args = ( filename, 1, width, height, 2, psycopg2.Binary(f.getvalue()), t['id'], 1, parent_id )
        #cur2 = query( qry, args, cursor = cur2 )
        write_to_disk( f, filename, height, width, t['id'], 2, parent_id, 1, 1 )
        f.close()

    #then we need to write our banner.
    cur = query( q, cursor = cur )
    for t in cur.fetchall():
        f = StringIO.StringIO()
        banner = im.copy()

        banner_box = ( int(float(request.form['banner_x'])), int(float(request.form['banner_y'])), int(float(request.form['banner_x']) + float(request.form['banner_width'])), int(float(request.form['banner_y']) + float(request.form['banner_height'])) )
        banner = banner.crop ( banner_box )
       
        width = int( t['max_height']) * float(request.form['banner_aspect'])
        height = int(t['max_height'])

        banner.thumbnail( (width, height), Image.ANTIALIAS )
        banner.save( f, 'JPEG' )

        #args = ( filename, 1, width, height, 3, psycopg2.Binary(f.getvalue()), t['id'], 1, parent_id )
        #cur2 = query( qry, args, cursor = cur2 )
        write_to_disk( f, filename, height, width, t['id'], 3, parent_id, 1, 1 )
        f.close()
    
    rmv_file( filename )
    return json( status = 'OK' )


@app.route('/my-account/upload/', methods = ['GET', 'POST'])    #FIXME: give this end point a better name.
def index():
	return render_template('upload.html')


@app.route('/my-galleries/', methods = ['GET', 'POST'])
def my_gallery_list():
    return render_template('my-galleries.html')


@app.route('/create-gallery/', methods = ['GET', 'POST'])
def my_gallery_create():
    pass


@app.route('/login/', methods = ['GET', 'POST'])
def login():
    username = None
    password = None
    email = None

    if 'username' in request.args:
        username = request.args['username']
    elif 'username' in request.form:
        username = request.form['username']

    if username is not None and '@' in username:
        email = username
        username = None

    if 'password' in request.args:
        password = request.args['password']
    elif 'password' in request.form:
        password = request.form['password']

    if username and password:
        qry = '''SELECT firstname, surname, id, public_email, private_email, member_type, website, username FROM member WHERE username = %s and password = pgp_sym_encrypt( %s, %s ) LIMIT 1;'''
        args = ( username, password, app.config['SECRET_KEY'] )
    elif email and password:
        qry = '''SELECT firstname, surname, id, public_email, private_email, member_type, website, username FROM member WHERE private_email = %s and password = pgp_sym_encrypt( %s, %s ) LIMIT 1;'''
        args = ( email, password, app.config['SECRET_KEY'] )
    else:
        return json( error = True, message = 'invalid login credentials.')
    cur = query( qry, args )
    res = cur.fetchone()
    if res:
        session['info'] = res.copy()
        return json( message = 'Success!' )
    return json( error = True, message = 'invalid username or password.' )


@app.route('/logout/', methods = ['GET', 'POST'])
def logout():
    if 'info' in session:
        session.pop('info', {})
    return json( message = 'successfully logged out.' )


## Functions
def gen_location(location = None):
    cmd = '''/bin/mkdir -p %s'''
    if location:
        cmd = cmd % (app.config['TEMP_FOLDER']+location)
    else:
        cmd = cmd % (app.config['TEMP_FOLDER'])
    Popen( shlex.split(cmd) )


def rmv_file( filename ):
    cmd = '''/bin/rm %s'''
    args = ( app.config['TEMP_FOLDER']+filename+'.tmp' )
    cmd = cmd % args
    Popen( shlex.split( cmd ) )


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in [ 'png', 'jpeg', 'jpg', 'bmp', 'tiff' ]

if __name__ == '__main__':
	app.run('0.0.0.0', port = 8181, debug= True)
