import sys
import os
import re
import json
import shutil
from cStringIO import StringIO
from FormHandler import FormHandler
from FileHandler import FileHandler
from crawler2 import validate
from crawler2 import crawler
from PIL import Image
# from PIL import ImageFile
# ImageFile.LOAD_TRUNCATED_IMAGES = True


formhandler = FormHandler()
filehandler = FileHandler()

absolutePath = os.path.expanduser("~")
file_absolute_path = absolutePath + "/Workspaces/Resources/Boxes/"

def upload(environ,start_response):
    formlist = formhandler.getFormDataAsList(environ)
    filedata, parameters = formhandler.parseFormDataList(formlist)
    filename = formhandler.getFileName(formlist[1])
    filehandler.saveFileFromFormData(filedata,filename,file_absolute_path)
    #fixme: unalble to generate thumbnial, got turncated error.
    im = Image.open(file_absolute_path+filename)
    # im.thumbnail((128,128))
    x, y = im.size
    w, h = int(x*0.2), int(y*0.2)
    if w < 128:
        w = 128
    if h < 128:
        h = 128
    im = im.resize((w,h))
    thumbnail_Image_path = filehandler.insertSubPath(-1,file_absolute_path+filename,"thumbnails")
    thumbnail_path = filehandler.removePathComponet(-1,thumbnail_Image_path)
    if not filehandler.isDirExists(thumbnail_path):
        os.makedirs(thumbnail_path)
    im.save(thumbnail_Image_path)

    response_body = '{\"status\": \"1\",\"action\":\"'+ file_absolute_path+filename + '\"}'
    start_response('200 OK',[('Content-Type','text/html'),('Content-Length',str(len(response_body)))])
    return [response_body]

def download(environ,start_response):
    response_body = ''
    response_length = ''
    formdatas = formhandler.getFormDatas(environ)
    formdatalist = formdatas.split('&')
    #print 'real datas::: '+formdatas
    path = ''
    isThumbnailPrefered = 0
    for element in formdatalist:
        key, value = element.split('=')
        if key == 'PATH':
            path = value
        if key == 'ThumbnailPrefered':
            isThumbnailPrefered = value

    head, tail = os.path.split(path)
    isfile = bool(tail.strip())

    if not isfile:
        #request is not for a specific file but a directory
        #try to return the directory list
        dir = file_absolute_path + path
        try:
            list = os.listdir(dir)
            list = [elem for elem in list if not elem[0]=="."]
            for name in list:
                #detect broken symlink
                linkpath = dir+name
                if os.path.islink(linkpath):
                    target_path = os.readlink(linkpath)
                    if not os.path.exists(target_path):
                        list.remove(name)
                        os.unlink(linkpath)

        except os.error:
            response_body = '{\"status\": \"0\",\"action\":\"/service/download\",\"description\":' \
                            + 'No permission to list directory' + '}'
            return response_body
        filelist = json.dumps(list)
        response_body = '{\"status\": \"1\",\"action\":\"/service/download\",\"results\":' + filelist + '}'

    else:
        #it is file, try to download it.
        filepath = file_absolute_path+path
        if os.path.islink(filepath):
            link_path = os.readlink(filepath)
            if not os.path.exists(link_path):
                os.unlink(filepath)
        try:
            finallyFilePath = filepath

            if isThumbnailPrefered:
                fileThumbnailPath = filehandler.insertSubPath(-1,filepath,"thumbnails")  # a/b/c.jpg -> a/b/thumbnail/c.jpg
                if filehandler.isFileExists(fileThumbnailPath):
                    finallyFilePath = fileThumbnailPath

            file_size = os.path.getsize(finallyFilePath)
            response_length = str(file_size)
            file_stream = file(finallyFilePath,'r')
            response_body = environ['wsgi.file_wrapper'](file_stream)

        except:
            #no such file or permission deny
            response_body = '{\"status\": \"0\",\"action\":\"/service/download\",\"description\":' \
                            + 'No such file or permission deny' + '}'
            start_response('404 Not Found',[('Content-Type','text/html'),('Content-Length',str(len(response_body))),('Access-Control-Allow-Origin','*')])
            return response_body

    if not response_length:
        response_length = str(len(response_body))

    start_response('200 OK',[('Content-Type','text/html'),('Content-Length',response_length),('Access-Control-Allow-Origin','*')])
    return response_body


def get_thumbnails(environ,start_response):

    formdatas = formhandler.getFormDatas(environ)
    formdatalist = formdatas.split('&')
    path = ''
    for element in formdatalist:
        key, value = element.split('=')
        if key == 'PATH':
            path = value
            break

    head, tail = os.path.split(path)
    isfile = bool(tail.strip())
    if isfile:
        havefile = filehandler.isFileExists(file_absolute_path+path)
        if not havefile:
            #thumbnail does not exists
            #try to access a fold by filename
            #why: because the only reason why there is missing thumb
            #is because you create a new folder, so we access this folder
            #grab the thumbnail of his children as his own.
            print 'thumb is missing at '+file_absolute_path+path
            #this pattern will grab the file name as a folder name
            #and store the previous folder name as well
            pattern = r'(.*)/*thumbnails/(.+)\.jpg'
            folder_name_match = re.search(pattern,path)
            if folder_name_match:
                folder = folder_name_match.group(2)
                prefolder = folder_name_match.group(1)
                dummy_path = file_absolute_path+prefolder+folder+'/thumbnails'
                dummy_list = os.listdir(dummy_path)
                for file in dummy_list:
                    if file[-4:] == '.jpg':
                        #wala, find a dummy for use
                        dummy_thumb_path = dummy_path + '/'+file
                        #make the link
                        command = 'ln -s '+dummy_thumb_path.replace(' ','\ ')+' '+file_absolute_path+path.replace(' ','\ ')
                        print command
                        os.system(command)
                        break
            else:
                start_response('404 Not Found',
                               [('Content-Type','text/html'),('Access-Control-Allow-Origin','*')])
                return ['{\"status\": \"0\",\"action\":\"/service/getthumbnails\",\"description\":file not exists}']

        return download(environ,start_response)

    else:
        start_response('404 Not Found\n no such file',[('Content-Type','text/html'),('Access-Control-Allow-Origin','*')])
        return '',


def move(environ,start_response):
    formDatas = formhandler.getFormDatas(environ)
    formDatasList = formDatas.split('&')

    for element in formDatasList:
            src, dst = element.split('=')
            valid_src_path = file_absolute_path+src.replace(' ','\ ')
            valid_dst_path = file_absolute_path+dst.replace(' ','\ ')

            valid_src_thumb_path = filehandler.insertSubPath(-1,valid_src_path,"thumbnails")
            valid_dst_thumb_path = filehandler.insertSubPath(-1,valid_dst_path,"thumbnails")
            try:
                os.system('mv ' + valid_src_path + ' ' + valid_dst_path)
                os.system('mv ' + valid_src_thumb_path + ' ' + valid_dst_thumb_path)
                print "EXE: mv "+ valid_src_path + ' ' + valid_dst_path
                print "ExE: mv "+ valid_src_thumb_path+ ' '+ valid_dst_thumb_path
            except:
                print 'invalid move operation'

    body = '{\"status\":\"1\",' \
            '\"action\":\"/service/move\",' \
            '\"item\":\"'+src+'\"}'
    length = str(len(body))
    start_response('200 OK',[("Content-Type","text/html"),("Content-Length",length),('Access-Control-Allow-Origin','*')])
    return [body]

def delete(environ, start_response):
    form_data = formhandler.getFormDatas(environ)
    form_data_list = form_data.split('&')

    #print form_data_list

    for element in form_data_list:
        id, filename = element.split('=')
        del_path = file_absolute_path+filename
        filehandler.deleteFile(file_absolute_path+filename)
        filehandler.deleteFile(filehandler.insertSubPath(-1,del_path,"thumbnails"))#delete thumb here
        print "delete: "+file_absolute_path+filename

    body = '{\"status\": \"1\",\"action\":\"/service/delete\"}'
    length = str(len(body))
    start_response('200 OK', [("Content-Type","text/html"),("Content-Length",length)])
    return [body]

def replace(environ, start_response):
    formDatas = formhandler.getFormDatas(environ)
    formDatasList = formDatas.split('&')
    operationPath = {}
    for element in formDatasList:
        id, filename = element.split('=')
        operationPath[id]=file_absolute_path + filename;

    shutil.copyfile(operationPath['PATH'], operationPath['DESTINATION_PATH'])

    body = '{\"status\": \"1\",\"action\":\"/service/delete\"}'
    length = str(len(body))
    start_response('200 OK', [("Content-Type","text/html"),("Content-Length",length)])
    return [body]

def getpatrolconfig(environ,start_response):
    '''
    1. grab files list in config folder.
    2. sort the list.
    3. binary search for nearest file.
    3. return file content.
    '''


    #This is binary search based on integer
    def binsearchpos(arr,key,start,end):
        midpos = (end + start + 1)/2
        mid = arr[midpos]
        if mid == key:
            return midpos
        elif mid < key:
            #search right
            if midpos+1 > end:
                return end
            else:
                return binsearchpos(arr,key,midpos+1,end)
        elif mid > key:
            #search left
            if midpos-1 < start:
                return start-1
            else:
                return binsearchpos(arr,key,start,midpos-1)

    formdatas = formhandler.getFormDatas(environ)
    time = formdatas.split('=')[1]
    time = int(time[:-4].replace('-',''))
    #todo:validation the time format as yyyy-mm-dd
    if time:
        dir = file_absolute_path+'Security/Patrol/config/'
        #grab list from folder
        list = os.listdir(dir)
        #filter list
        list = [elem for elem in list if elem[-4:]==".txt"]
        #sorted...which is easy
        list.sort()
        callist = [int((elem[:-4]).replace('-','')) for elem in list]
        pos = binsearchpos(callist,time,0,len(list)-1)

        #handle the filename to download app
        filename = list[pos]
        downloadpath = "PATH=Security/Patrol/config/"+filename
        environ['wsgi.input'] = StringIO(downloadpath)
        environ['CONTENT_LENGTH'] = str(len(downloadpath))
        return download(environ,start_response)

    start_response('500 ERROR',[("Content-Type","text/html"),('Access-Control-Allow-Origin','*')])
    return ['error']

def getfilesize(environ, start_response):
    formDatas = formhandler.getFormDatas(environ)
    filepath = formDatas.split('=')[1]
    if filepath:
        size = os.path.getsize(file_absolute_path+filepath)
        if size:
            response_body = '{\"status\": \"1\",\"action\":\"/service/filesize\",\"results\":' + str(size) + '}'
            start_response('200 OK',[('Content-Type','text/html'),("Content-Length",str(len(response_body))),('Access-Control-Allow-Origin','*')])
            return [response_body]
    start_response('404 NOT FOUND',[('Content-Type','text/html'),('Access-Control-Allow-Origin','*')])
    return ['error']

def gettrackfile(environ,start_response):
    return download(environ,start_response)

def rename(environ, start_response):
    formdatas = formhandler.getFormDatas(environ)
    formlist = formdatas.split('&')
    for pair in formlist:
        src,dst =  pair.split('=')
        real_src = file_absolute_path + src
        real_dst = file_absolute_path + dst
        print 'mv '+ real_src + ' ' + real_dst
        os.system('mv '+ real_src.replace(' ','\ ') + ' ' + real_dst.replace(' ','\ '))
    start_response('200 OK', [("Content-Type","text/html"),('Access-Control-Allow-Origin','*')])
    return ['ok']

def struct(environ, start_response):
    formdata = formhandler.getFormDatas(environ)
    key, val = formdata.split('=')
    result_dic = crawler(file_absolute_path+val, validate(file_absolute_path+val+"/.ignore"))
    start_response('200 OK',[("Content-Type","text/html"),('Access-Control-Allow-Origin','*')])
    return [json.dumps(result_dic)]


def createFolder(environ, start_response):
    formdatas = formhandler.getFormDatas(environ)
    parts = formdatas.split('&')
    path = None
    pwd = None
    for part in parts:
        key, val = part.split('=')
        if key == 'path':
            path = val
        elif key == 'pwd':
            pwd = val

    real_create_path = file_absolute_path + path
    os.mkdir(real_create_path)
    real_thumb_path = real_create_path + "/thumbnails"
    os.mkdir(real_thumb_path)

    if pwd:
        newf = open(real_create_path+'/.password','w')
        newf.write(pwd+'\n')
    start_response('200 OK',[("Content-Type","text/html"),('Access-Control-Allow-Origin','*')])
    return ['ok']

