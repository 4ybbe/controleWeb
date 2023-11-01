import sys
import smtplib, ssl

bdFail = []
for i in sys.argv:
    bdFail.append(i)

#FORMATACAO
bdFail.remove(bdFail[0])   
bdFalhou = str(bdFail)
bdFalhou = bdFalhou.replace("[", "")
bdFalhou = bdFalhou.replace("]", "")
bdFalhou = bdFalhou.replace("'", "")

#SMTP INFO
port = 587  
smtp_server = "xxxxxxxxx"
login = "xxxxxxxxx"
password = "xxxxxxxxx"
sender_email = "xxxxxxxxx"
emails_to = ["email@gmail.com", "email2@gmail.com"] 
message = """\
Subject: Falha ao realizar o backup do Banco de Dados 

Os seguintes bancos falharam ao realizar o backup ou possuem o tamanho menor que o dia anterior:
"""+ bdFalhou +"""
"""


with smtplib.SMTP(smtp_server, port) as server:
    server.starttls()
    server.login(login, password)
    for email in emails_to:
        server.sendmail(sender_email, email, message)
    server.quit()

