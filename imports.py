#! /usr/bin/python

from flask import Flask, render_template, request, Response, url_for, abort, send_from_directory, g, jsonify
from werkzeug import secure_filename
import PIL
from PIL import Image #https://pillow.readthedocs.org/handbook/tutorial.html
import logging, shlex, shutil
from subprocess import Popen

import cStringIO as StringIO
import psycopg2, psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from random import shuffle
