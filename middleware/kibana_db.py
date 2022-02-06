import os
import json
import sys
import time
import uuid
import socket

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

import middleware
from imglabeling.librarys import delete_imgfile
from django.db import connection

class DatabaseErrorMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):

        if 'db' in str(exception.__class__):

            if connection:
                connection.rollback()

            connection.close()


