#! /usr/bin/python
from imports import *
from flask import current_app as app

def json( data = {}, message = None, status = 'OK', error = False ):
    response = {}
    if status is not None:
        if error:
            status = 'Error'
        response['status'] = status
    if message is not None:
        response['message'] = message
        if error:
            response['error'] = message
    response['results'] = data

    return jsonify(response)


def connect():
    con = psycopg2.connect( database = app.config['DB_NAME'],
        host = app.config['DB_HOST'], 
        user = app.config['DB_USER'], 
        password = app.config['DB_PASSWORD'], 
        port = app.config['DB_PORT'],
        cursor_factory = psycopg2.extras.DictCursor )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) #FIXME: do commits in the query function etc.
    return con


def query( qry, args = None, cursor = None ):
    if not cursor:
        cursor = g.con.cursor()
    try:
        logging.debug ( cursor.mogrify( qry, args ) )
        cursor.execute( qry, args )
        return cursor
    except Exception, e:
        logging.exception('Error occurred with query' )
	print e
        return None


def serve_from_disk( id ):
	logging.debug( id )
	image_type = None
	image_size = None
	if '_' in id: #FIXME make use of regex and groups..
		image_type = id[id.find('_')+1:]
		id = id[:id.find('_')]
		if '_' in image_type:
			image_size = image_type[image_type.find('_')+1:]
			image_type = image_type[:image_type.find('_')]
	try:
		id = int(id)
	except:
		abort(404)
	directory = '1/%d/' #FIXME hardcoded magic number.
	args = ( id, )
	if image_type:
		directory = directory + '%d/'
		args = args + ( int(image_type), )
	else:
		directory = directory + '1/'
	imagename = 'f'
	if image_size:
		imagename = image_size
	elif image_type:
		imagename = 'l'
	return send_from_directory( app.config['IMAGE_FOLDER'] + directory % args, imagename, as_attachment = False, mimetype = 'image/jpeg' ) 

	
def serve_from_db( id ):
    logging.debug(id)
    image_type = None
    image_size = None
    if '_' in id:
        image_type = id[id.find('_')+1:]
        id = id[:id.find('_')]
        if '_' in image_type:
            image_size = image_type[image_type.find('_')+1:]
            image_type = image_type[:image_type.find('_')]

    isint = True
    try:
        id = int(id)
    except:
        isint = False

    WHERE = None
    qargs = (id, )
    if image_type or image_size:
        WHERE = 'WHERE parent_image = %s'
    else:
        WHERE = 'WHERE id = %s'
    if image_type:
        WHERE = WHERE + ' AND thumb_type = %s'
        qargs = qargs + ( image_type, )
    if image_size:
        WHERE = WHERE + ' AND image_size = (SELECT id FROM image_size WHERE appendix = %s)'
        qargs = qargs + ( image_size, )

    qry = '''SELECT image FROM image %s LIMIT 1''' % ( WHERE, )
    cur = query( qry, qargs )
    rw = cur.fetchone()
    if not rw:
        logging.debug('Image Not Found.')
        abort(404)
    return Response( rw[0], mimetype = 'image/jpeg' )


def write_to_db( image, imagename, image_height, image_width, image_size, thumb_type, parent_id = None, author_id = 1, gallery_id = 1 ):
	qry = '''INSERT INTO image ( image_name, author_id, image_width, image_height, thumb_type, image, image_size, gallery_id, parent_image ) 
	VALUES 
(%s,%s,%s,%s,%s,%s,%s,%s, %s) RETURNING id;'''
	args = ( imagename, author_id, image_width, image_height, thumb_type, psycopg2.Binary( image.getvalue() ), image_size, gallery_id, parent_id )
	cur = query( qry, args )
	if cur:
		return cur.fetchone()[0]
	return None


def write_to_disk( image, imagename, image_height, image_width, image_size, thumb_type, parent_id = None, author_id = 1, gallery_id =1 ):
	cmd = '''/bin/mkdir -p %s'''
	directory = app.config['IMAGE_FOLDER'] + '''%d/%d/%d/'''
	id = parent_id
	qry = '''INSERT INTO image ( image_name, author_id, image_width, image_height, thumb_type, image_size, gallery_id, parent_image ) 
	VALUES
 (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id;'''
	args = ( imagename, author_id, image_width, image_height, thumb_type, image_size, gallery_id, parent_id )
	cur = query( qry, args )
	if not cur:
		return None
	insertion = cur.fetchone()[0]
	if not id:
		id = insertion
	cur = query( '''SELECT appendix from image_size WHERE id = %s''', ( image_size, ), cur )
	args = ( author_id, int(id), int(thumb_type) )
	Popen( shlex.split( cmd % ( directory % args ) ) )
	i = 99999
	while i > 0:
		i -=1
	with open( (directory + cur.fetchone()[0]) % args, 'w+' ) as fd:
		image.seek(0)
		shutil.copyfileobj( image, fd )
	return insertion	
