#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Import modules for CGI handling 
# Import modules for CGI handling 
import cgi, cgitb 
import os
from modules.logintools import login
from modules.configobj import ConfigObj
from modules.pathutils import *
import urllib
from modules.coptic_sql import *

def make_options(**kwargs):
    if "file" in kwargs:
        names = open(kwargs["file"],'r').read().replace("\r","").split("\n")
        #print len(names)
        names = list(name[:name.find("\t")] for name in names)
    elif "names" in kwargs:
        names = kwargs[names]
    selected = kwargs["selected"] if "selected" in kwargs else None
    options=""
    for name in names:
        if name!='':
            options+='<option value=%s>\n' %name
    return options

def cell(text):
    return "<td>" + str(text) + "</td>"

def get_max_id():
    #get current max of existing records in the db
    current_max=generic_query("SELECT MAX(id) AS max_id FROM coptic_docs",())[0][0]
    #set the max key for auto_increment of id to that value
    generic_query("UPDATE sqlite_sequence SET seq=? WHERE name=?",(current_max,"coptic_docs"))
    return current_max


def gen_meta_popup():
    popup_meta_html="""
    <HTML>
    <HEAD>
    <SCRIPT LANGUAGE="JavaScript"><!--
    function copyForm() {
        opener.document.hiddenForm.metakey.value = document.popupForm.metakey.value;
        opener.document.hiddenForm.metavalue.value = document.popupForm.metavalue.value;

        opener.document.hiddenForm.submit();
        window.close();
        return false;
    }
    //--></SCRIPT>
    </HEAD>
    <BODY>
    <FORM NAME="popupForm" onSubmit="return copyForm()">
    meta key (e.g.,year):<br>
    <input list="metakeys" name="metakey">
    <datalist id="metakeys">
        ***options***
    </datalist>
    <br>
    meta value(e.g.,200BC):<br>
    <input type="text" name='metavalue'><br>
    <INPUT TYPE="BUTTON" VALUE="Submit" onClick="copyForm()">
    </FORM>
    </BODY>
    </HTML>


    """
    options=make_options(file='metadata_fields.tab')
    popup_meta_html=popup_meta_html.replace("***options***",options)
    f=open('popupPage.html','w')
    f.write(popup_meta_html)


def load_landing(theform):

    gen_meta_popup()

    if theform.getvalue('deletedoc'):
        docid=theform.getvalue('id')
        delete_doc(docid)

    #docs_list=generic_query("SELECT * FROM coptic_docs","")
    docs_list=generic_query("SELECT coptic_docs.id,name,status,username,filename FROM coptic_docs JOIN users ON coptic_docs.assignee_users_id=users.id",())

    max_id=get_max_id()
    
    #for each doc in the doc list, just display doc[:-1], since last col is content

    table="""<table><tr><th>id</th><th>doc name</th><th>status</th><th>assigned</th><th>filename</th><th>editing</th><th>deletion</th></tr>"""

    for doc in docs_list:
        row="<tr>"
        for item in doc:
            
            row+=cell(item)
        id=str(doc[0])
        #edit document
        button_edit="""<form action=editor.py method="post">"""
        id_code="""<input type="hidden" name="id"  value="""+id+">"
        button_edit+=id_code
        button_edit+="""<input type="submit" value="EDIT DOCUMENT"></form>    """

        #delete document
        button_delete="""<form action=landing.py method="post">"""
        button_delete+=id_code
        button_delete+="""<input type='submit' name='deletedoc'  value='DELETE DOCUMENT'></form>"""

        row+=cell(button_edit)
        row+=cell(button_delete)
        row+="</tr>"
        table+=row
        
    table+="</table>"

    page= "Content-type:text/html\r\n\r\n"
    page+="""

    <!DOCTYPE html>
    <html>
    <head>
    <style>
    table {
        font-family: arial, sans-serif;
        border-collapse: collapse;
        width:400pt;
    }

    td, th {
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
    }

    body{padding:10pt;}

    </style>
    </head>
    <body>

    <h1 >Coptic XML transcription editor</h1>
        <p style="border-bottom:groove;"><i>created by Shuo Zhang and Amir Zeldes</i></p>

    <h2>Welcome!</h2>


    """

    create_new_doc = """\n\n\n<form action='editor.py'><input type="hidden" name="id" value="""+str(max_id+1)+">"  
    create_new_doc+=""" <input type="hidden" name="newdoc" value='true'>    """
    create_new_doc+= """<input type="submit" value="create new document"> </form>"""
    
    admin_page="""\n<form action='admin-coptic.py'> <input type='submit' value='admin'></form>
    """

    page+=admin_page
    page+=table
    page+="<br><br>"
    page+=create_new_doc
    page+='\n</body>\n</html>'
    
    return page





def open_main_server():
    thisscript = os.environ.get('SCRIPT_NAME', '')
    action = None
    theform = cgi.FieldStorage()
    scriptpath = os.path.dirname(os.path.realpath(__file__)) + os.sep
    userdir = scriptpath + "users" + os.sep
    action, userconfig = login(theform, userdir, thisscript, action)
    print load_landing(theform)




open_main_server()




