import re
from os import listdir
from os.path import isfile, join, abspath, exists
import json


def validate(configfile):
    '''
    this method read config file which
    include the file styles we want to ignore
    just like .gitignore
    '''
    f = open(configfile)
    #each line as a regular expression
    regs = [e[:-1] for e in f.readlines()]

    def check(filename):
        for e in regs:
            if re.match(e, filename):
                return False
        return True

    return check


def crawler(path, filter, pwd=None):
    '''
    this method walks through all level start from the given path
    make the entire structure into a nested dic.
    '''
    if not filter(path): return None
    f = isfile(path)
    if f:
        name = path.split('/')[-1][:-4]
    else:
        name = path.split('/')[-1]

    curlevel = {name: {}}
    # curlevel[name]['path'] = path
    curlevel[name]['name'] = name
    curlevel[name]['pwd'] = pwd
    curlevel[name]['date'] = None

    if not f:
        password_path = path+"/.password"
        if exists(password_path):
            f = open(password_path)
            _pwd =  f.readline()
            pwd = _pwd
            curlevel[name]['pwd'] = _pwd
        contents = {}
        contents_list = [crawler(join(path, p), filter, pwd) for p in listdir(path) if filter(p)]
        # curlevel[name]['content'] = {crawler(join(path,p),filter) for p in listdir(path) if filter(p)}
        for outter in contents_list:
            key = outter.keys()[0]
            contents[key] = outter[key]
        curlevel[name]['content'] = contents


    return curlevel


class jsonOperator(object):
    def __init__(self, _json):
        self.json_file = _json
        self.json_dict = json.loads(self.json_file)

    def index_path_visitor(self, dic, index_path):
        paths = index_path.split('.')
        tar = dic
        for path in paths:
            tar = tar[path]
        return tar

    def get(self, index_path):
        result = self.index_path_visitor(self.json_dict, index_path)
        return json.dumps(result)

    def remove(self, index_path):
        paths = index_path.split('.')
        if len(paths) <= 1:
            print "too few to remove"
            return False
        new_index_path = '.'.join(paths[:-1])
        level = self.index_path_visitor(self.json_dict, new_index_path)
        try:
            result = dict(level[paths[-1]])
            del level[paths[-1]]
            return result
        except:
            print "delete failed"
            return False

    def add(self, index_path, newdic):
        paths = index_path.split('.')
        name = paths[-1]
        new_index_path = '.'.join(paths[:-1])
        level = self.index_path_visitor(self.json_dict, new_index_path)
        level[name] = newdic

    def move(self, src_index_path, dst_index_path):
        src = self.remove(src_index_path)
        self.add(dst_index_path, src)

# result = crawler('BusinessCards', validate('.ignore'))
# jsonfile = json.dumps(result)
# print jsonfile
# operator = jsonOperator(jsonfile)
# print operator.move("BusinessCards.content.nihao","BusinessCards.content.Tough.content.nihao")
# print operator.get("BusinessCards")



# print result
