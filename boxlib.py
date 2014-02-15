import sys
import os
import re
import json
from FormHandler import FormHandler
from FileHandler import FileHandler

formhandler = FormHandler()
filehandler = FileHandler()

absolutePath = os.path.expanduser("~")
file_absolute_path = absolutePath + "/Workspaces/Resources/Boxes/"

def upload(environ,start_response):
    formlist = formhandler.getFormDataAsList(environ)
    filedata, parameters = formhandler.parseFormDataList(formlist)
    filename = formhandler.getFileName(formlist[1])
    filehandler.saveFileFromFormData(filedata,filename,file_absolute_path)
    response_body = '{\"status\": \"1\",\"action\":\"'+ file_absolute_path+filename + '\"}'
    start_response('200 OK',[('Content-Type','text/html'),('Content-Length',str(len(response_body)))])
    return [response_body,]

def download(environ,start_response):
    response_body = ''
    response_length = ''
    formdatas = formhandler.getFormDatas(environ)
    formdatalist = formdatas.split('&')
    print formdatas
    path = ''
    for element in formdatalist:
        key, value = element.split('=')
        if key == 'PATH':
            path = value
            break

    head, tail = os.path.split(path)
    isfile = bool(tail.strip())

    if not isfile:
        #request is not for a specific file but a directory
        #try to return the directory list
        dir = file_absolute_path+path
        try:
            list = os.listdir(dir)
        except os.error:
            response_body = '{\"status\": \"0\",\"action\":\"/service/download\",\"description\":' \
                            + 'No permission to list directory' + '}'
        filelist = json.dumps(list)
        response_body = '{\"status\": \"1\",\"action\":\"/service/download\",\"results\":' + filelist + '}'

    else:
        #it is file, try to download it.
        filepath = file_absolute_path+path
        print filepath
        try:
            file_size = os.path.getsize(filepath)
            response_length = str(file_size)
            file_stream = file(filepath,'r')
            response_body = environ['wsgi.file_wrapper'](file_stream)

        except:
            #no such file or permission deny
            response_body = '{\"status\": \"0\",\"action\":\"/service/download\",\"description\":' \
                            + 'No such file or permission deny' + '}'

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

        print environ
        return download(environ,start_response)

    else:
        start_response('404 Not Found\n no such file',[('Content-Type','text/html'),('Access-Control-Allow-Origin','*')])
        return '',


def move(environ,start_response):
    formDatas = formhandler.getFormDatas(environ)
    formDatasList = formDatas.split('&')

    for element in formDatasList:
            src, dst = element.split('=')
            os.system('ln -s ' + file_absolute_path+src.replace(' ','\ ') + ' ' + file_absolute_path+dst.replace(' ','\ '))
            print "EXE: ln "+ file_absolute_path+src + ' ' + file_absolute_path+dst
    #lastObject = formDatasList[-1]
    #lastValues = lastObject.split('=')
    body = '{\"status\": \"1\",\"action\":\"/service/move\"}'
    length = str(len(body))
    start_response('200 OK',[("Content-Type","text/html"),("Content-Length",length)])
    return [body]

def fetchconfig(environ,start_response):
    pass

def gettrackfile(environ,start_response):
    return download(environ,start_response)