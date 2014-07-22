
import re
import urllib
from cStringIO import StringIO

class FormHandler:
    def parseFormDataList(self, formDatasList):
        parameters = {}
        listLen = len(formDatasList)

        for index in range(2, listLen-1):
            itemname = self.getItemName(formDatasList[index])
            itemvalue = self.getItemValue(formDatasList[index])
            parameters[itemname] = itemvalue

        #for key, value in parameters.items():
            #print key + ' : ' + value

        #for line in formDatasList:
            #print line

        fileDataRaw = formDatasList[1][:-2]

        #print fileDataRaw

        fileDataVerbose = fileDataRaw.split('Content-Type:')[1]

        #print fileDataVerbose

        indexVerbose = fileDataVerbose.find('\r\n\r\n')

        #print str(indexVerbose)

        result = fileDataVerbose[indexVerbose+4:]

        #print result

        return result, parameters

    def getFormDatas(self, environ):

        body = ''
        try:
            length = int(environ.get('CONTENT_LENGTH', '0'))
        except ValueError:
            length = environ['wsgi.input'].default_bufsize
        if length != 0:
            body = StringIO(environ['wsgi.input'].read(length))
            environ['wsgi.input'] = body
        return body.getvalue()

    def getFormDataAsList(self, environ):
        formDatas = self.getFormDatas(environ)
        boundary_content = self.getFormBoundary(environ)
        formDatasList = formDatas.split(boundary_content)
        return formDatasList

    def getFormBoundary(self, environ):
        content_type = environ['CONTENT_TYPE']
        boundary_key_str = 'boundary='
        boundary_key_len = len(boundary_key_str)
        boundary_index = content_type.index(boundary_key_str)
        boundary_content = content_type[boundary_index + boundary_key_len:]
        return boundary_content

    def getBoundaryLength(self, environ):
        return len(self.getFormBoundary(environ))

    def getFileName(self, fileFormDatas):
        file_name_list = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', fileFormDatas)
        #print 'this is form: '+ fileFormDatas
        #print 'end of form'
        file_name = file_name_list[0]
        return file_name

    def getItemName(self, itemFormDatas):
        item_name_list = re.findall(r'.*name="(.*)"', itemFormDatas)
        item_name = item_name_list[0]
        return item_name

    def getItemValue(self, itemFormDatas):
        item_value_list = re.findall(r'name=.*\r\n(.*)\r\n', itemFormDatas, re.DOTALL)
        item_value = item_value_list[0]
        return item_value
