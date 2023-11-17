from lxml import etree
from xml.etree import ElementTree
from gvm.connections import TLSConnection, SSHConnection 
from gvm.protocols.latest import Gmp
from gvm.transforms import EtreeTransform
from gvm.xml import pretty_print

# connection = SSHConnection(hostname='223.193.36.146', port=2222, timeout=25, username='test', password='test')
connection = TLSConnection(hostname='223.193.36.57', port=9390, cafile='./cacert.pem', certfile='./clientcert.pem', keyfile='./clientkey.pem')
transform = EtreeTransform()
with Gmp(connection, transform=transform) as gmp:

    gmp.authenticate('admin','admin')

    version = gmp.get_version()
    pretty_print(version)
    # Retrieve all tasks
    tasks = gmp.get_tasks()

    # Get names of tasks
    task_names = tasks.xpath('task/name/text()')
    pretty_print(task_names)
    gmp.disconnect()
    # connection.disconnect()