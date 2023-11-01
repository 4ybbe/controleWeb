from flask import Flask, redirect, render_template, request, make_response, send_file
import os
import psutil
import subprocess
import signal
import json
import time
import mysql.connector
import random
from datetime import date
import datetime
import socket
from pythonping import ping
import paramiko

app = Flask(__name__,
            static_folder=os.getcwd(),
            static_url_path='')

#TODO 
# PID NOT FOUND
# NOTIFICACAO - OK
# DOWNLOAD - OK
# FILTRO

pidDir = os.getcwd() + '/pidlista/'
empresaDir = os.getcwd() + '/empresaconf/'
empresalista = os.getcwd() + '/empresalista/listadict.json'
pclista = os.getcwd() + '/empresalista/pcstatus.json'
backupjson = os.getcwd() + '/backupjson/backup.json'
checkstatus = os.getcwd() + '/checkstatus/sgLista/'
downloadDir = os.getcwd() + '/downloads/'
backupScript = os.getcwd() + '/mailPy/'

class startUtil():     
    def dictStart():
        tableData = []
        pcData = [{'cpu' : 'Inativo',
                   'memper' : 'Inativo',
                   'memmb' : 'Inativo'}]
        
        for arquivo in os.listdir(empresaDir):
            service = {"empresa" : arquivo,
                        "prcwin" : "Inativo",
                        "servidor": "Inativo",
                        "api": "Inativo",
                        "agendador": "Inativo"}
            tableData.append(service)
            
        cloud = {'servidor' : 'backup',
                'host': 'backup',
                'datahora' : 'backup',
                'pastaarquivo' : 'backup',
                'nomearquivo' : 'backup',
                'tamanhoarquivo' : 'backup'}  
        
        with open(empresalista, 'w') as jason:
            json.dump(tableData, jason, indent=4)
        CmdUtil.statusSg() 

        with open(pclista, 'w') as jason:
            json.dump(pcData, jason, indent=4)
        CmdUtil.statusMaquina()
        
        with open(backupjson, 'w') as jason:
            json.dump(cloud, jason, indent=4)

        with open (empresalista, 'r') as tmpstart:
            tableData = json.load(tmpstart)
            return tableData         

class onlineUtil():
    def sgStatus():
        with open(checkstatus + 'jsonSgLista','r+') as file:
            data = json.load(file)
    
            for empresa in data:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    result = sock.connect_ex((empresa['IP'], int(empresa['PORTA'])))
                    if result == 0:
                        empresa["Online"] = "Online"
                    else:
                        empresa["Online"] = "Offline"
                except:
                    empresa["Online"] = "Offline"
                
                try:
                    ping_res = ping(empresa['IP'], count=3, timeout=1)
                    empresa["Latencia"] = str(ping_res.rtt_avg_ms)
                except:
                    empresa["Latencia"] = "Offline"
                file.truncate(0)
                file.seek(0)
                json.dump(data, file)    
            
        with open (checkstatus + 'jsonSgLista','r') as statusServ:
            sgData = json.load(statusServ)
            return sgData 
        
    def serverStatus():
        with open(checkstatus + 'jsonServerLista','r+') as file:
            data = json.load(file)
    
            for empresa in data:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((empresa['IP'], int(empresa['PORTA'])))
                if result == 0:
                    empresa["Online"] = "Online"
                else:
                    empresa["Online"] = "Offline"
                ping_res = ping(empresa['IP'], count=3, timeout=1)
                empresa["Latencia"] = str(ping_res.rtt_avg_ms)
                file.truncate(0)
                file.seek(0)
                json.dump(data, file)    
            
        with open (checkstatus + 'jsonServerLista','r') as statusServ:
            serverData = json.load(statusServ)
            return serverData 
        
    def registerSgStatus():
        url = request.form['url-register']
        ip = request.form['ip-register']
        porta = request.form['porta-register']   
        data = {
            'URL': url,
            'IP': ip,
            'PORTA': porta,
            'Latencia': '0',
            'Online': 'Online'
            }  
        with open(checkstatus + 'jsonSgLista','r+') as file:
            file_data = json.load(file)
            file_data.append(data)
            file.seek(0)
            json.dump(file_data, file, indent = 4) 
            
    def registerServerStatus():
        url = request.form['urlsrv-register']
        ip = request.form['ipsrv-register']
        porta = request.form['portasrv-register']   
        data = {
            'URL': url,
            'IP': ip,
            'PORTA': porta,
            'Latencia': '0',
            'Online': 'Online'
            }  
        with open(checkstatus + 'jsonServerLista','r+') as file:
            file_data = json.load(file)
            file_data.append(data)
            file.seek(0)
            json.dump(file_data, file, indent = 4) 
        
class backupUtil():
    def connectMysql():
        conn = mysql.connector.connect(user='xxxxxx', password='xxxxxx', database='xxxxxx' , host='xxxxx')
        return conn
    
    def cloudBackup():   
        cloud = []
        hoje = date.today()
        conn = backupUtil.connectMysql()
        cursor = conn.cursor()
        query = (f"SELECT * FROM `tb_backup` ") #WHERE datahora LIKE '{hoje}%'")    
        cursor.execute(query)
        
        rows = cursor.fetchall()
        for backup in rows:
            dicionario = {
                'servidor': backup[0],
                'host': backup[1],
                'datahora': backup[2],
                'pastacaminho': backup[3],
                'nomearquivo': backup[4],
                'tamanhoarquivo': backup[5],
                'nome_bd': backup[6],
                'sv_destino': backup[7]
            }
            cloud.append(dicionario)
        return cloud
    
    def checkBackup():
        bdFail = []
        t = datetime.datetime.now()
        hoje = date.today()
        conn = backupUtil.connectMysql()
        with open (os.getcwd() + '/backupjson/bds', 'r') as checkbd:
            checkbd = checkbd.readlines()
        for bd in checkbd:
            bd = bd.strip()
            cursor = conn.cursor()
            query = (f"SELECT * FROM `tb_backup` WHERE nome_bd = '{bd}' AND datahora LIKE '{hoje}%' ")
            cursor.execute(query)
            rows = cursor.fetchall()
            if len(rows) == 0:
                bdFail.append(bd)          #BD QUE NAO FOI FEITO BACKUP
        for bd in checkbd:
            try:
                bd = bd.strip()
                cursor = conn.cursor()
                query = (f"SELECT tamanhoarquivo FROM `tb_backup` WHERE datahora >= NOW() - INTERVAL 2 DAY AND nome_bd = '{bd}' AND servidor = (SELECT servidor FROM tb_backup WHERE datahora >= NOW() - INTERVAL 1 DAY AND nome_bd = '{bd}' LIMIT 1); ") #ONTEM
                cursor.execute(query)
                rows = cursor.fetchall()
                #FORMATACAO
                sizeontem = rows[0]
                sizeontem = str(sizeontem).replace("/MB", "")
                sizeontem = sizeontem.replace("',)", "")
                sizeontem = sizeontem.replace("('", "")
                sizehoje = rows[1] 
                sizehoje = str(sizehoje).replace("/MB", "")
                sizehoje = sizehoje.replace("',)", "")
                sizehoje = sizehoje.replace("('", "")
                if sizeontem > sizehoje:
                    bdFail.append(bd)
                if sizehoje == '':
                    bdFail.append(bd)    
            except:
                bdFail.append(bd)
        if len(bdFail) != 0:
            bdFalhou = str(bdFail)
            bdFalhou = bdFalhou.replace("[", "")
            bdFalhou = bdFalhou.replace("]", "")
            bdFalhou = bdFalhou.replace("'", "")
            bdFalhou = bdFalhou.replace(",", " ")
            os.system(f'python3 {backupScript}emails.py {bdFalhou}')
  
    def registerBackup():
        t = datetime.datetime.now()
        hoje = date.today()
        conn = backupUtil.connectMysql()
        cursor = conn.cursor()
        query = (f"SELECT `nome_bd` FROM `tb_backup` ")
        cursor.execute(query)
        rows = cursor.fetchall()
        for bd in rows:
            bd = str(bd)
            bd = bd.replace("(", "")
            bd = bd.replace(")", "")
            bd = bd.replace(",", "")
            bd = bd.replace("'", "")
            with open (os.getcwd() + '/backupjson/bds', 'r') as checkbd:
                checkbd = str(checkbd.readlines())
                if not bd in checkbd:
                    with open (os.getcwd() + '/backupjson/bds', 'a') as appendbd:
                        appendbd.write(bd + '\n')
                else:
                    pass
    
    def registrarDados(servidor, iphost, pastaarquivo, nomearquivo, tamanhoarquivo, nome_bd , sv_destino):
        conn = mysql.connector.connect(user='xxxxxx', password='xxxxxxx', database='xxxxxx' , host='xxxxxxxx')
        cursor = conn.cursor()
        query = (f"INSERT INTO tb_backup "
             "(servidor, host, datahora, pastaarquivo, nomearquivo, tamanhoarquivo, nome_bd, sv_destino) " 
             f"VALUES ('{servidor}', '{iphost}', sysdate(), '{pastaarquivo}', '{nomearquivo}', '{tamanhoarquivo}', '{nome_bd}', '{sv_destino}')")
    
        cursor.execute(query)
        conn.commit()

    def downloadBackup(file):
        host = '192.168.1.201'
        usersftp ='xxxxxxx'
        passwdsftp ='xxxxxx'
        port=2244
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=host,port=port,username=usersftp,password=passwdsftp)
        ftp = ssh_client.open_sftp()
        ftp.get(f"/cloud/{file}", downloadDir + file)
        ftp.close()
        ssh_client.close()
    
    def clearBackup():
        try:
            for file in os.listdir(downloadDir):
                os.remove(downloadDir + file)
        except:
            pass
               
class loginUtil():
    def setCookie():
        cookie = str(random.randint(999, 69636))
        with open (os.getcwd() + '/sessoes/' + cookie, 'w') as sessao:
            resp = make_response(redirect('/home'))
            userAgent = request.headers.get('User-Agent')
            iprcv = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)   
            sessao.write(userAgent + '\n')
            sessao.write(iprcv)
            sessao.close()
            resp.set_cookie('sessao', cookie)
            return resp
        
    def checkCookie():
        acesso = False
        cookie = request.cookies.get('sessao')
        for sessao in os.listdir(os.getcwd() + '/sessoes/'):
            if acesso != True:
                with open (os.getcwd() + '/sessoes/' + sessao, 'r') as check:
                    tmp = check.readlines()
                    if cookie in sessao:
                        userAgent = request.headers.get('User-Agent')
                        iprcv = request.environ.get('HTTP_X_REAL_IP', request.remote_addr) 
                        if userAgent and iprcv in tmp:
                            acesso = True
                        else:
                            acesso = False
                    else:
                        acesso = False
            else:
                return acesso  
        return acesso   
    
    def resetSession():
        for sessao in os.listdir(os.getcwd() + '/sessoes/'):
            os.remove(os.getcwd() + '/sessoes/' + sessao)      
  
class CmdUtil():
    def addEmp():
        empresa = request.form['empresa-register']
        prcwin = request.form['prcwin-register']
        servidor = request.form['servidor-register']
        with open (empresaDir + empresa, 'w') as tmpadd:
            tmpadd.write(empresa + '\n')
            tmpadd.write(prcwin + '\n')
            tmpadd.write(servidor + '\n')
            try:
                api = request.form['apiprcwin-register']
                tmpadd.write(api + '\n')
            except:
                pass
            try:
                agendador = request.form['agendador-register']
                tmpadd.write(agendador + '\n')
            except:
                pass 
            try:
                porta = request.form['porta-register']
                tmpadd.write(porta + '\n')
            except:
                pass
            tmpadd.close()
        os.remove(empresalista)
        startUtil.dictStart()

    def startSg(servico):
        with open(pidDir + servico, 'w') as resetpid:
            resetpid.write('')
            resetpid.close()
        with open(empresaDir + '/' + servico, 'r') as startsc:
            tmp = startsc.readlines()     
            for processo in tmp:
                with open(pidDir + servico, 'a') as regpid:
                    if 'servidor' in processo:
                        x = tmp.index(processo)
                        prc = tmp[x].strip()
                        pidsv = subprocess.Popen("wine servidor.exe", cwd=prc, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
                        regpid.write(str(pidsv.pid) + '\n')
                        time.sleep(3)
                    if 'api' in processo:
                        x = tmp.index(processo)
                        prc = tmp[x].strip()
                        pidapi = subprocess.Popen("wine Apiprcwin.exe", cwd=prc, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
                        regpid.write(str(pidapi.pid) + '\n')
                    if os.path.isfile(processo.strip() + 'prcwin.exe'):
                        x = tmp.index(processo)
                        prc = tmp[x].strip()
                        pidsg = subprocess.Popen("wine prcwin.exe", cwd=prc, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid) 
                        regpid.write(str(pidsg.pid) + '\n')
                    if os.path.isfile(processo.strip() + 'Agendadorprcwin.exe'):
                        x = tmp.index(processo)
                        prc = tmp[x].strip()
                        pidagenda = subprocess.Popen("wine Agendadorprcwin.exe", cwd=prc, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid) 
                        regpid.write(str(pidagenda.pid) + '\n')
                regpid.close()

    def stopSg(servico):
        with open (pidDir + '/' + servico, 'r') as stopsc:
            tmp = stopsc.readlines()
            for pidlinha in tmp:
                pidkill = psutil.Process(int(pidlinha))
                for child in pidkill.children(recursive=True):
                    child.kill()
                pidkill.kill()
                #Segunda tentativa
                try:
                    os.kill(int(pidlinha), signal.SIGTERM)
                except:
                    pass
        with open (empresaDir + '/' + servico, 'r') as stopfuser:
            tmp = stopfuser.readlines()
            for linha in tmp:
                try:
                    #900X
                    tmp = str(linha)
                    linha = tmp.replace('\n', '')
                    os.system(f'fuser -k {linha}/tcp')
                    #800X
                    tmp = str(linha)
                    tmp = tmp.replace('\n', '')
                    tmp = list(tmp)
                    tmp[0] = '8'
                    linha = ''.join(tmp)
                    os.system(f'fuser -k {linha}/tcp')
                    #700X
                    tmp = str(linha)
                    tmp = tmp.replace('\n', '')
                    tmp = list(tmp)
                    tmp[0] = '7'
                    linha = ''.join(tmp)
                    os.system(f'fuser -k {linha}/tcp')
                except:
                    pass

        os.remove(pidDir + '/' + servico)
        os.system('reset')
        time.sleep(5)

    def statusSg(): 
        with open (empresalista, 'r') as arquivo:
            data = json.load(arquivo)
        for emp in os.listdir(pidDir):
            with open (pidDir + emp, 'r') as stts:
                tmp = stts.readlines()
                for linha in tmp:
                    try:
                        prc = psutil.Process(int(linha))
                        mem = prc.memory_percent()
                        cpu = prc.cpu_percent(interval=None)
                        for child in prc.children(recursive=True):
                            mem += child.memory_info().rss / (1024 * 1024)
                            cpu += child.cpu_percent()
                            if 'prcwin' in child.name():
                                for empresa in data:
                                    if empresa['empresa'] == emp:
                                        empresa['prcwin'] = ("%.2f" % mem) + "MB /" + ("%.2f" % cpu) + "%"
                            if 'Api' in child.name():
                                for empresa in data:
                                    if empresa['empresa'] == emp:
                                        empresa['api'] = ("%.2f" % mem) + "MB /" + ("%.2f" % cpu) + "%"
                            if 'servidor' in child.name():
                                for empresa in data:
                                    if empresa['empresa'] == emp:
                                        empresa['servidor'] = ("%.2f" % mem) + "MB /" + ("%.2f" % cpu) + "%"
                            if 'Agendador' in child.name():
                                for empresa in data:
                                    if empresa['empresa'] == emp:
                                        empresa['agendador'] = ("%.2f" % mem) + "MB /" + ("%.2f" % cpu) + "%"
                    except psutil.NoSuchProcess:
                        for empresa in data:
                            if empresa['empresa'] == emp:
                                empresa['prcwin'] = 'PID não encontrado'
                                empresa['api'] = 'PID não encontrado'
                                empresa['servidor'] = 'PID não encontrado'
                                empresa['agendador'] = 'PID não encontrado'
                    
        with open(empresalista, 'w') as arquivo:
            json.dump(data, arquivo, indent=4)
        
    def statusMaquina(): 
        with open (pclista, 'r') as arquivo:
            data = json.load(arquivo)

        memMB = int(psutil.virtual_memory().total - psutil.virtual_memory().available)
        memMB = '{} MB'.format(int(memMB / 1024 / 1024))
        memPER = psutil.virtual_memory().percent
        cpu = psutil.cpu_percent(interval=0.5)

        data = {
            'cpu': str(cpu) + "%",
            'memper': str(memPER) + "%",
            'memmb': str(memMB)
        }
                
        with open(pclista, 'w') as arquivo:
            json.dump(data, arquivo, indent=4)

        with open (pclista, 'r') as tmpstart:
            pcdata = json.load(tmpstart)
            return pcdata


@app.route('/status', methods=['POST', 'GET'])
def statusz():
    if request.method == 'GET':
        acesso = loginUtil.checkCookie()   #AUTH
        if acesso == False:
            resp = make_response(redirect('/'))
            return resp
        else:
            sgData = onlineUtil.sgStatus()
            serverData = onlineUtil.serverStatus()
            return render_template('status.html', sgData=sgData, serverData=serverData)
    if request.method == 'POST':
        if "add" in request.form:
            onlineUtil.registerSgStatus()
            resp = make_response(redirect('/status'))
            return resp
    if request.method == 'POST':
        if "addaddmysql" in request.form:
            onlineUtil.registerServerStatus()
            resp = make_response(redirect('/status'))
            return resp
        
        
    else:
        return render_template('404.html')     

@app.route('/download/<string:info_nomearquivo>', methods=['GET', 'POST'])
def down(info_nomearquivo):
    if request.method == 'GET':
        acesso = loginUtil.checkCookie()  #AUTH
        if acesso == False:
            resp = make_response(redirect('/'))
            return resp
        else:
            backupUtil.clearBackup()
            backupUtil.downloadBackup(info_nomearquivo)
            pathfile = downloadDir + info_nomearquivo
            return send_file(pathfile, as_attachment=True)
    else:
        return render_template('404.html')  

@app.route('/backup', methods=['GET', 'POST'])
def bak():
    if request.method == 'GET':
        acesso = loginUtil.checkCookie()   #AUTH
        if acesso == False:
            resp = make_response(redirect('/'))
            return resp
        else:
            bck = backupUtil.cloudBackup()
            return render_template('backup.html', bck=bck)  
    
@app.route('/statusregistrar/', methods=['POST', 'GET'])   
def statusreg():
    if request.method == 'POST':
        usuario = request.args["user"]
        senha = request.args["pass"]
        if (usuario == 'statusprcwin') and (senha == 'status!1bh'):
            ip           = request.args["ip"]
            conn         = request.args["conn"]
            onlineUtil.pingCheck(ip, conn)
            resp = make_response(redirect('/home'))
            return resp
        else:
            return render_template('404.html')  
    else:
        return render_template('404.html') 
    
@app.route('/registrar/', methods=['POST', 'GET'])
def regist():
    if request.method == 'POST':
        usuario = request.args["user"]
        senha = request.args["pass"]
        if (usuario == 'prcwin') and (senha == 'prcwin'):
            servidor       = request.args["servidor"]
            iphost         = request.args["host"]
            pastaarquivo   = request.args["pastaarquivo"]
            nomearquivo    = request.args["nomearquivo"]
            tamanhoarquivo = request.args["tamanhoarquivo"] 
            nome_bd        = request.args["nome_bd"] 
            sv_destino     = request.args["sv_destino"] 
            backupUtil.registrarDados(servidor, iphost, pastaarquivo, nomearquivo, tamanhoarquivo, nome_bd, sv_destino)    
            resp = make_response(redirect('/home'))
            return resp
        else:
            return render_template('404.html')  
    else:
        return render_template('404.html')  

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if "login" in request.form:
            usuario = request.form['login-user']
            senha = request.form['login-pass']
            if (usuario == 'suporte') and (senha == 'suporte'): 
                resp = loginUtil.setCookie()
                return resp
            else:
                loginUtil.resetSession()
                resp = make_response(redirect('/'))
                return resp
    if request.method == 'GET':
        return render_template('login.html')
    else:
        return render_template('404.html')  
    
@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        acesso = loginUtil.checkCookie()  #AUTH
        if acesso == False:
            resp = make_response(redirect('/'))
            return resp
        else:
            tableData = startUtil.dictStart()
            pcData = CmdUtil.statusMaquina()
            return render_template('index.html' , tableData=tableData, pcData=pcData)
    if request.method == 'POST':
        if "add" in request.form:
            CmdUtil.addEmp()
        resp = make_response(redirect('/home'))
        return resp
    else:
        return render_template('404.html')  
        
@app.route('/checkbackup', methods=['GET', 'POST'])
def checkBackupTime():
    if request.method == 'GET':
        resp = make_response(redirect('/404'))
        return resp
    if request.method == 'POST':
        passwd = request.headers.get('User-Agent')
        if passwd == '438IF96YW':
            backupUtil.registerBackup()
            backupUtil.checkBackup()
            resp = make_response(redirect('/'))
            return resp
    else:
        return render_template('404.html')  
    
@app.route('/start/<string:info_empresa>')
def start(info_empresa):
    CmdUtil.startSg(info_empresa)
    resp = make_response(redirect('/home'))
    return resp

@app.route('/stop/<string:info_empresa>')
def stop(info_empresa):
    CmdUtil.stopSg(info_empresa)
    resp = make_response(redirect('/home'))
    return resp

@app.route('/reload/<string:info_empresa>')
def reload(info_empresa):
    CmdUtil.stopSg(info_empresa)
    CmdUtil.startSg(info_empresa)
    resp = make_response(redirect('/home'))
    return resp


if __name__ == '__main__':
    loginUtil.resetSession()
    app.run(host="127.0.0.1" , debug=True)

        
