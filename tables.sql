/* Tables File */

BEGIN;

DROP TABLE IF EXISTS member_type;
CREATE TABLE member_type ( id SERIAL PRIMARY KEY NOT NULL, 
	name TEXT
);

INSERT INTO member_type ( name ) VALUES ( 'User' );
INSERT INTO member_type ( name ) VALUES ( 'Author' );
INSERT INTO member_type ( name ) VALUES ('Admin' );

DROP TABLE IF EXISTS member;
CREATE TABLE member ( id SERIAL PRIMARY KEY NOT NULL,
	firstname TEXT,
	surname TEXT,
	public_email TEXT,
	private_email TEXT UNIQUE,
	member_type INTEGER NOT NULL REFERENCES member_type(id),
	biography TEXT,
	website TEXT,
	username TEXT UNIQUE,
	password BYTEA
);


INSERT INTO member ( firstname, private_email, member_type ) VALUES ('callum', 'cdt60@hotmail.com', 3 );
INSERT INTO member ( firstname, private_email, member_type ) VALUES ('Jacob', 'jacob.o@windowslive.com', 3);

DROP TABLE IF EXISTS gallery;
CREATE TABLE gallery ( id SERIAL PRIMARY KEY NOT NULL,
	name TEXT,
	author_id INTEGER NOT NULL REFERENCES member(id),
	about TEXT,
	visible BOOLEAN DEFAULT FALSE
);
--FIXME need a trigger that creates a gallery on each author+ member add.
INSERT INTO gallery ( name, author_id, visible ) VALUES ( 'Test', 1, True );

DROP TABLE IF EXISTS image_type;
CREATE TABLE image_type ( id SERIAL PRIMARY KEY NOT NULL,
	name TEXT
);

INSERT INTO image_type ( name ) VALUES ( 'Original' );
INSERT INTO image_type ( name ) VALUES ( 'Thumb' ); 
INSERT INTO image_type ( name ) VALUES ( 'Banner' );

DROP TABLE IF EXISTS image_size;
CREATE TABLE image_size ( id SERIAL PRIMARY KEY NOT NULL,
	name TEXT,
	max_height INTEGER,
	appendix CHAR(1)
);

INSERT INTO image_size ( name, max_height, appendix ) VALUES ( 'Tiny', 100, 't' );
INSERT INTO image_size ( name, max_height, appendix ) VALUES ( 'Small', 320, 's' );
INSERT INTO image_size ( name, max_height, appendix ) VALUES ( 'Medium', 720, 'm' ); 
INSERT INTO image_size ( name, max_height, appendix ) VALUES ( 'Large', 1080, 'l' ); 
INSERT INTO image_size ( name, max_height, appendix ) VALUES ( 'Full', NULL, 'f' ); --Full/Original Image.

DROP TABLE IF EXISTS image;
CREATE TABLE image ( id SERIAL PRIMARY KEY NOT NULL,
	image_name TEXT,
	author_id INTEGER NOT NULL REFERENCES member(id),
       	image_width INTEGER,
	image_height INTEGER,
	thumb_type INTEGER NOT NULL REFERENCES image_type(id),
	image_size INTEGER NOT NULL REFERENCES image_size(id),
	image bytea,
	parent_image INTEGER REFERENCES image(id), --This is always the full original image.
	gallery_id INTEGER NOT NULL REFERENCES gallery(id),
	visible BOOLEAN DEFAULT FALSE,
	CONSTRAINT file_location UNIQUE ( image_name, thumb_type, image_size, parent_image, author_id )
);

DROP TABLE IF EXISTS image_note;
CREATE TABLE image_note (
	image_id INTEGER REFERENCES image(id),
	note TEXT,
	title TEXT,
	UNIQUE(image_id)
); /*we want to be able to join this on image_id OR parent_image, rather than have it on the image table.*/

DROP TABLE IF EXISTS tag;
CREATE TABLE tag ( id SERIAL PRIMARY KEY NOT NULL,
	name TEXT
);

DROP TABLE IF EXISTS image_tag;
CREATE TABLE image_tag (
	image_id INTEGER NOT NULL REFERENCES image(id),
	tag_id INTEGER NOT NULL REFERENCES tag(id),
	PRIMARY KEY(image_id, tag_id)
);

CREATE EXTENSION IF NOT EXISTS pgcrypto;

COMMIT;
