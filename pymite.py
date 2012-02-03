import subprocess
import sys
import pmImgCreator
from SerialConnection import SerialConnection
from settings import PATH_TO_PYMITE, PATH_TO_DFU_UTIL



def loadtoipm(src, BAUD, PORT):
    pmfeatures_file = PATH_TO_PYMITE + '/src/platform/stm32f2/pmfeatures.py'
    pmfeatures = pmImgCreator.PmImgCreator(pmfeatures_file)
    code = compile(src, '', "exec")
    img = pmfeatures.co_to_str(code)
    print len(img)
    conn = SerialConnection(PORT, BAUD)
    conn.write(img)    
    return ''.join([c for c in conn.read()])

# need threads
def Compile():
    text = subprocess.Popen('scons PLATFORM=stm32f2', cwd = PATH_TO_PYMITE, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
    if len(text)>1: res = '\n'.join([t.strip() for t in text[1:]])
    else: res = text[0]
    return res

    
# need threads
def LoadDfu():
    #  add SYSFS{idVendor}=="0483", SYSFS{idProduct}=="df11", MODE="666" GROUP="plugdev" SYMLINK+="usb/stm32_dfu"
    #  to plugdev (in Debian, I just created a new file in the /etc/udev/rules.d directory with this single line in it. Locations may be slightly different in other Linux distributions).
    text = subprocess.Popen(PATH_TO_DFU_UTIL + 'dfu-util --device 0483:df11 --alt 0 --dfuse-address 0x08000000 --download ' + PATH_TO_PYMITE + '/src/platform/stm32f2/main.bin', shell=True, stdout=subprocess.PIPE).stdout.readlines()
    if len(text)>1: res = '\n'.join([t.strip() for t in text[1:]])
    else: res = text[0]
    return res
