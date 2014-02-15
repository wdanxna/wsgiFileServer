
import os
import errno
import re
import time

currentPath = os.path.realpath(__file__)
parentPath = os.path.abspath(os.path.join(currentPath, os.pardir))

class FileHandler:
    # def getIndexTemplate(self):
            #currentPath = os.getcwd()
            #currentPath = os.path.realpath(__file__)
            #parentPath = os.path.abspath(os.path.join(currentPath, os.pardir))
            #htmlFilePath = parentPath + '/template'
            # return open(htmlFile).read()

    def saveFileFromFormData(self, fileData, file_name, file_path):
        configpattern = r'.*config.txt'
        config_match = re.search(configpattern,file_name)
        if config_match:
            currentDate =  time.strftime('%Y-%m-%d',time.localtime(time.time()))

        self.saveFile(fileData, file_name, file_path)

    def saveFile(self, file_data, file_name, file_path):
        file_path_name = file_path + file_name

        name = os.path.basename(file_path_name)
        path = file_path_name.replace(name, "")

        if not os.path.exists(path):
            print 'creating: '+ path
            os.makedirs(path)


        file_upload = open(file_path_name, 'w')
        file_upload.write(file_data)
        file_upload.flush()
        file_upload.close()

    def deleteFile(self, file_path, file_name):
        file_path_name = file_path + file_name
        #if os.path.exists(file_path_name):
            #os.remove(file_path_name)
        try:
            os.remove(file_path_name)
        except OSError, e: # this would be "except OSError as e:" in python 3.x
            if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
                raise # re-raise exception if a different error occured

    def removeEmptyFolders(self, path):
        if not os.path.isdir(path):
            return
        # remove empty subfolders
        files = os.listdir(path)
        if len(files):
            for f in files:
                fullpath = os.path.join(path, f)
                if os.path.isdir(fullpath):
                    self.removeEmptyFolders(fullpath)

        # if folder empty, delete it
        files = os.listdir(path)
        if len(files) == 0:
            print "Removing empty folder:", path
            os.rmdir(path)

    def isFileExists(self, path_to_file):
        if os.path.isfile(path_to_file):
            try:
               with open(path_to_file): pass
            except IOError:
               return 0
        else:
            return 0
        return 1

    def isDirExists(self, path):
        return os.path.isdir(path) and os.path.exists(path)

    def handleData(self,formHandler,filepath, environ):
        #print '#### --> handleData thread id is : ' + str(threading.current_thread().ident)
        formDatasList = formHandler.getFormDataAsList(environ)
        fileData, parameters = formHandler.parseFormDataList(formDatasList)
        print 'form list'
        print formDatasList
        print 'form list end'
        file_name = formHandler.getFileName(formDatasList[1])
        print '#### --> has  parsed form data successfully'


        self.saveFileFromFormData(fileData, file_name, filepath)
        print '######## a file upload absolute path : ' + filepath + '  file name : ' + file_name
        return filepath + file_name
