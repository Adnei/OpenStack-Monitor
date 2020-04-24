from modules.objects import db_info as DB_INFO
from modules.objects.os_image import *
from modules.objects.service import *
from modules.objects.execution import *
from modules.objects.operation import *
from modules.objects.metering import *
from modules.objects.packet_info import *
from modules.objects.request_info import *


DB_INFO.BASE.metadata.create_all()
