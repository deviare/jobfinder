import argparse
from time import sleep
import textwrap
import sys
from modules import linkedin, get_mails, mailer



def parse_command_line():

    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog=textwrap.dedent(
                '''
                Format for credentials in command line argument or in file:
                username:password

                Format for target jobs in command line argument of file (evrey line):
                job:city
                
                Format for file smtp credentials:
                username:password:server:port

                '''
                )
            )

    group_job = parser.add_mutually_exclusive_group(required=True)
    group_job.add_argument("-r",  dest="path_jobs",  help="path to file with target jobs")
    group_job.add_argument("-j",  dest="job", help="job and city target [job:city]", action="append")

    group_creds = parser.add_mutually_exclusive_group(required=True)
    group_creds.add_argument("-l", dest="creds", help="username and password linkedin account [username:password]")
    group_creds.add_argument("-c", dest="path_creds", help="path to file with credentials")
    
    group_mail= parser.add_argument_group()
    group_mail.add_argument("-a", default=False, action='store_true', help="apply to jobs sending an email, reqired -M, -C, -A")
    group_mail.add_argument("-C", help="path to file with credentials smp server")
    group_mail.add_argument("-M", help="path to file with email body")
    group_mail.add_argument('-A', help='path to file to attach (Curriculum)')


    parser.add_argument("-H", help="run it not headless (show browser)", default=True, action="store_false")

    return parser



def set_args():
    
    argument = parse_command_line().parse_args()
    headless=argument.H
    smtp={}

    if argument.creds is None:
        with open(argument.path_creds, 'r') as f:
            lines=f.readlines()
            for line in lines:
                if not line.startswith(" "):
                    creds=line
    
    elif argument.path_creds is None:
        creds=argument.creds


    if argument.job is None:
        with open(argument.path_jobs, 'r') as f:
            target=f.readlines()

    elif argument.path_jobs is None:
        target[0]=argument.job


    if argument.a:
        if argument.C is None or argument.m is None or argument.A is None:
            print('[-] Error: to send the mail all arguments -a, -C, -M, -A are required')
            sys.exit(1)
    
        else:
            with open(argument.C, 'r') as f:
                smtp_user, smtp_pass, smtp_server, smtp_port = f.readline().split(':')
            
            mail_path=argument.M
            atach_path=argument.A
            smtp={
                    'user':smtp_user,
                    'pass':smtp_pass,
                    'server':smtp_server,
                    'port':smtp_port,
                    'mail_path':mail_path,
                    'atach_path':atach_path
                    }
    args={
            'creds':creds,
            'target':target,
            'headless':headless,
            'smtp':smtp
            }
    
    return args


def run_mailer(args):
    user=args['user']
    password=args['pass']
    server=args['server']
    port=args['port']
    mail_path=args['mail_path']
    atach_path=['atach_path']
    mailer = mailer.Mailer(user, password, server, port, mail_path, atach_path)
    mailer.send_mails()



def run_bot():
    args=set_args()
    username=args['creds'].split(':')[0]
    password=args['creds'].split(':')[1]
    headless=args['headless']
    targets=args['target']
    print("[+] Starting Selenium WebDriver [+]")
    linked=linkedin.linkedin(username, password, headless) 
    linked.login()

    for trg in targets:
        job, city =trg.split(':')
        linked.look_for_jobs(job, city)
        sleep(5)
        linked.get_urls(linked.extract_company())
    linked.close_driver()
    print("[+] Crowling founded sites for email address [+]")
    get_mails.main()
    print('[+] E-mail address written to ./emails.txt [+]')
    
    if  args['smtp']:
        print('[+] Starting to sending mail [+]')
        run_mailer(args['smtp'])
        
    else:
        sys.exit(0)


if __name__=="__main__":
    run_bot()






