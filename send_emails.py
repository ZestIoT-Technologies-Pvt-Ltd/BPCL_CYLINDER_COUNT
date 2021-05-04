
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import smtplib
from datetime import datetime


class send_csv_file:
    ''' Sends mail from 'raja@zestiot.io' to specified users '''
    def send_mail(self, text, subject, toaddress, files, names, main_ = None, cc=None,bcc=None):
        msg = MIMEMultipart()
        msg['From'] = 'Venkata@zestiot.io'
        if main_:
            msg['To'] = ",".join(main_)
        if cc:
            msg['CC'] = ",".join(cc)
        if bcc:
            msg['BCC'] = ",".join(bcc)
        if not main_ and not cc and not bcc:
            msg['To'] = ",".join(toaddress)
        msg['Subject'] = subject
        msg.attach(MIMEText(text, 'html'))
        if files:
            for file, name in zip(files, names):
                attachment = open(file, "rb")
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-Disposition', "attachment; filename= %s" % name)
                msg.attach(p)
        try:
            mailserver = smtplib.SMTP('smtp.office365.com', 587)
            mailserver.ehlo()
            mailserver.starttls()
            mailserver.login('Venkata@zestiot.io', 'Maggi@21')
            mailserver.sendmail('Venkata@zestiot.io', toaddress, msg.as_string())
            mailserver.quit()
        except Exception as e:
            print(e)
            pass
        
        


        
def legend_presentation(Legend):

    def row_to_html(row):
        st = ''' <Tr> '''
        for act in list(row):
            st = st + '''<Td> {} </Td> '''.format(act)
        return st  + ''' </Tr> '''
    st = ''' </br><h2>Description of Unloading activities</h2> <Table border = '1px solid black' style="width:100%","text-align:center"> <Tr>'''

    for col in list(Legend.columns):
        st = st + '''<Th bgcolor = '#c0392b'> {} </Th>'''.format(col)
    st = st + '''</Tr>'''
    

    for index, rwx in Legend.iterrows():
        st = st + row_to_html(rwx)
    #st = st + 
    st = st + '''</Table>'''
    st = st + ''' </br>Regards <Tr> '''
    st = st + ''' </br>System Generated <Tr> '''
    return st





df = pd.read_csv("file.csv")
print(df)
read_csv_file = legend_presentation(df)
print(read_csv_file)
subject = "BPCL Unloading Point-3 Report on" +" "+datetime.today().strftime('%Y-%m-%d')
toaddress = ["Venkata@zestiot.io","saisurya@zestiot.io"]
files = ["file.csv"]
names = ["20210320"]

mail_obj = send_csv_file()

send_data = mail_obj.send_mail(read_csv_file, subject, toaddress, files, names, main_ = None, cc=None,bcc=None)


