"""
oVirt Live Plugin

The purpose of this plugin is to attach ISO domain,
upload there basic ISO files and to create a VM.
"""

import logging
import glob
import os
import os.path
import urllib2
import traceback
import basedefs
import common_utils as utils
import output_messages
import shutil
from ovirtsdk.xml import params

# Override basedefs default so that status message are aligned
basedefs.SPACE_LEN = 80

# Product version
MAJOR = '3'
MINOR = '2'

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "oLive"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)


# INFO Messages
INFO_CONF_PARAMS_ALL_IN_ONE_USAGE = "Configure all in one"
INFO_CONF_PARAMS_ALL_IN_ONE_PROMPT = "Configure VDSM on this host?"
INFO_CONF_PARAMS_LOCAL_STORAGE = "Local storage domain path"
INFO_LIBVIRT_START = "libvirt service is started"
INFO_CREATE_HOST_WAITING_UP = "Waiting for the host to start"
INFO_CREATE_VM_WAITING_DOWN = "Waiting for the vm to become down"
INFO_CREATE_VM_WAITING_UP = "Waiting for the vm to become up"
INFO_DISK_WAITING_OK = "Waiting for disk creation"

# ERROR MESSAGES
SYSTEM_ERROR = "System Error"
ERROR_CREATE_API_OBJECT = "Error: could not create ovirtsdk API object"
ERROR_CREATE_VM = "Error: Could not create VM"
ERROR_START_VM = "Error: Could not start VM"
ERROR_VM_DOWN_TIMEOUT = "Error: Timed out while waiting for vm to become down"
ERROR_VM_UP_TIMEOUT = "Error: Timed out while waiting for vm to become up"
ERROR_DISK_OK_TIMEOUT = "Error: Timed out while waiting for disk creation"
ERROR_JBOSS_STATUS = "Error: There's a problem with JBoss service.\
Check that it's up and rerun setup."

ERROR_ATTACH_ISO = "Error: Could not attch ISO domain"

# PARAMS
PAUSE = 10
SLEEP_PERIOD = 25 # period in seconds, this is waiting until JBoss is up
MAX_CYCLES = 33 # (5.5 (minutes) * 60 )/ 10, since we sleep 10 seconds after each iteration
LOCAL_STORAGE_MIN_SIZE = 10 # Size in Gb
API_OBJECT_PATH = "https://%s:%s/api"
JBOSS_HEALTH_URL = "http://%s:%s/OvirtEngineWeb/HealthStatus"
HOST_NAME = "local_host"

# Connection Settings
URL = 'https://localhost:443/api'
USERNAME = 'admin@internal'
PASSWORD = 'oVirt!'

DC_NAME = 'local_datacenter'
CLUSTER_NAME = 'local_cluster'
HOST_NAME = 'local_host'
STORAGE_NAME = 'local_storage'
EXPORT_NAME = 'local_export'
VM_NAME = 'local_vm'

ISO_PATH = '/usr/local/ovirt/data'
ISO_NAME = 'ISO'
LOCAL_STORAGE = "local_storage"
VM_DISK_NAME = 'local_vm_Disk1'

# PATH PARAMS
VDSM_PATH = "/usr/share/vdsm"

MB = 1024*1024
GB = 1024*MB

HADOW_FILE = "/etc/shadow"

logging.debug("plugin %s loaded", __name__)


def initConfig(controllerObject):
    # Set the controller object properly
    global controller
    controller = controllerObject
    pass

def initSequences(controller):
    logging.debug("Setting the Sequences for oVirt Live plugin")

    # Main oVirt Live sequences
    olSteps = [ { 'title'     : "%s: Attaching ISO Domain" % PLUGIN_NAME_COLORED,
                   'functions' : [attachIsoDomain] },
                { 'title'     : "%s: Copy Fedora CD" % PLUGIN_NAME_COLORED,
                   'functions' : [loadIsoFiles]},
                { 'title'     : "%s: Creating VM" % PLUGIN_NAME_COLORED,
                   'functions' : [createVm]}]

    logging.debug("Adding sequence to create host")
    controller.addSequence("oVirt Live", ["yes"], ["yes"], olSteps)

def returnYes(controller):
    return "yes"

def waitForJbossUp():
    """
    Wait for Jboss to start
    """
    utils.retry(isHealthPageUp, tries=25, timeout=15, sleep=5)

def attachIsoDomain():
    global controller
    logging.debug("Attaching ISO Domain")
    try:
        if not controller.CONF["API_OBJECT"].datacenters.get(DC_NAME).storagedomains.add(controller.CONF["API_OBJECT"].storagedomains.get(ISO_NAME)):
            raise Exception("Failed to attach iso storage domain")

        if not controller.CONF["API_OBJECT"].datacenters.get(DC_NAME).storagedomains.get(ISO_NAME).activate():
           raise Exception("Failed to activate iso storage domain")
    except:
        logging.error(traceback.format_exc())
        raise Exception(ERROR_ATTACH_ISO)

def loadIsoFiles():
    global controller
    logging.debug("Adding files to iso domain")
    isoPattern = "/home/liveuser/oVirtLiveFiles/iso/*.iso"
    fileList = glob.glob(isoPattern)

    # Prepare the full path for the iso files
    targetPath = os.path.join(controller.CONF["NFS_MP"], controller.CONF["sd_uuid"], "images", "11111111-1111-1111-1111-111111111111")

    try:
        # Iterate the list and copy all the files
        for filename in fileList:
            moveFile(filename, targetPath, basedefs.CONST_VDSM_UID, basedefs.CONST_KVM_GID)
    except:
        # We don't want to fail the setup, just log the error
        logging.error(traceback.format_exc())
        logging.error(output_messages.ERR_FAILED_TO_COPY_FILE_TO_ISO_DOMAIN)

def moveFile(filename, destination, uid=-1, gid=-1, filemod=-1):
    """
    copy filename to
    the destDir path
    give the target file uid:gid ownership
    and file mod

    filename     - full path to src file (not directories!)
    destination  - full path to target dir or filename
    uid          - integer with user id (default -1 leaves the original uid)
    gid          - integer with group id (default -1 leaves the original gid)
    filemod      - integer with file mode (default -1 keeps original mode)
    """
    # If the source is a directory, throw an exception since this func handles only files
    if (os.path.isdir(filename)):
        raise Exception(output_messages.ERR_SOURCE_DIR_NOT_SUPPORTED)

    # In case the src file is a symbolic link, we'll get the origin filename
    fileSrc = os.path.realpath(filename)

    # In default, assume the destination is a file
    targetFile = destination

    # Copy file to destination
    shutil.move(fileSrc, destination)
    logging.debug("successfully copied file %s to target destination %s"%(fileSrc, destination))

    # Get the file basename, if the destination is a directory
    if (os.path.isdir(destination)):
        fileBasename = os.path.basename(fileSrc)
        targetFile = os.path.join(destination, fileBasename)

    # Set file mode, uid and gid to the file
    logging.debug("setting file %s uid/gid ownership"%(targetFile))
    os.chown(targetFile, uid, gid)

    logging.debug("setting file %s mode to %d"%(targetFile, filemod))
    os.chmod(targetFile, filemod)


def createVm():
    global controller
    logging.debug("Creating VM")

    # Just to do api calls short
    api = controller.CONF["API_OBJECT"]

    try:
        # Defins OS param for the boot option
        os=params.OperatingSystem(type_='unassigned', boot=[params.Boot(dev='cdrom'), params.Boot(dev='hd')])

        # Create VM
        api.vms.add(params.VM(name=VM_NAME, memory=1*GB, os=os, cluster=api.clusters.get(CLUSTER_NAME), template=api.templates.get('Blank')))
        logging.debug("VM Created")

        # Create NIC
        api.vms.get(VM_NAME).nics.add(params.NIC(name='eth0', network=params.Network(name='ovirtmgmt'), interface='virtio'))
        logging.debug("NIC Created")

        # Create HD
        api.vms.get(VM_NAME).disks.add(params.Disk(storage_domains=params.StorageDomains(storage_domain=[api.storagedomains.get(STORAGE_NAME)]),
                                                   size=6*GB,
                                                   status=None,
                                                   interface='virtio',
                                                   format='cow',
                                                   sparse=True,
                                                   bootable=True))
        logging.debug("HD Created")

        # Wait for VM to become down
        # Down means HD was created
        logging.debug("Waiting for VM to become down")
        utils.retry(isVmDown, tries=100, timeout=500, sleep=5)
        logging.debug("Waiting for disk creation")
        utils.retry(isDiskOk, tries=100, timeout=500, sleep=5)

    except:
        logging.debug(traceback.format_exc())
        raise Exception(ERROR_CREATE_VM)

def startVm():
    global controller
    logging.debug("Starting VM")
    try:
        if controller.CONF["API_OBJECT"].vms.get(VM_NAME).status.state != 'up':

            # Start VM
            controller.CONF["API_OBJECT"].vms.get(VM_NAME).start()

            # Wait for VM up
            utils.retry(isVmUp, tries=100, timeout=500, sleep=5)
        else:
            logging.debug("VM Already up")
    except:
        logging.debug(traceback.format_exc())
        raise Exception(ERROR_START_VM)

def isDiskOk():
    logging.debug("Waiting for disk to be created")
    try:
        if controller.CONF['API_OBJECT'].vms.get("*").get_disks().get(name=VM_DISK_NAME).status.state != "ok":
            raise Exception(INFO_DISK_WAITING_OK)
        else:
            return
    except:
        logging.debug(traceback.format_exc())
        raise Exception(ERROR_DISK_OK_TIMEOUT)

def isVmDown():
    logging.debug("Waiting for VM to become down")
    try:
        if controller.CONF['API_OBJECT'].vms.get(VM_NAME).status.state != "down":
            raise Exception(INFO_CREATE_VM_WAITING_DOWN)
        else:
            return
    except:
        logging.debug(traceback.format_exc())
        raise Exception(ERROR_VM_DOWN_TIMEOUT)

def isVmUp():
    logging.debug("Waiting for VM start")
    try:
        if controller.CONF['API_OBJECT'].vms.get(VM_NAME).status.state != "up":
            raise Exception(INFO_CREATE_VM_WAITING_UP)
        else:
            return
    except:
        logging.debug(traceback.format_exc())
        raise Exception(ERROR_VM_UP_TIMEOUT)

def isHealthPageUp():
    """
    check if project health page is and accesible
    will throw exception on error
    and not return a value
    """
    health_url = JBOSS_HEALTH_URL % (controller.CONF["HOST_FQDN"], controller.CONF["HTTP_PORT"])
    logging.debug("Checking JBoss status.")
    content = getUrlContent(health_url)
    if content and utils.verifyStringFormat(content, ".*DB Up.*"):
        logging.info("JBoss is up and running.")
        return True
    else:
        logging.error(ERROR_JBOSS_STATUS)
        raise Exception(ERROR_JBOSS_STATUS)

def getUrlContent(url):
    try:
        urlObj = urllib2.urlopen(url)
        urlContent = urlObj.read()
    except:
        return None

    return urlContent

