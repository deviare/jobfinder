# jobfinder

This script scarp linkedin jobs offerts with Selenium,
then crawl each company sites looking for emails address using regex and save data in the database.
Optionaly can send mail to apply to the job, must provide credentials for smtp server, body text, and attachement (Curriculum) 

The program assume you have firefox and geckodriver installed respectively in /usr/bin/firefox-esr and /usr/local/bin/geckodriver
and you are using a *nix system 

The program is build to run with a linkedin account with italian lenguage.

Many things can go wrong with linkedin and Selenium, I will try to keep it updated
If you have problem during login, try to run it not headless (-H) possibly linkedin have reconize Selenium and ask for a captcha,
solve it and run it again.


# To Do

- [ ] Handle login with request to avoid selenium related problems 
- [ ] Sobstitute sleep call to WebDriverWait
- [ ] Fix bugs 

# usage
```
pip3 install -r requirements.txt
python3 jobfinder.py -h
usage: jobfinder.py [-h] (-r PATH_JOBS | -j JOB) (-l CREDS | -c PATH_CREDS)
                    [-a] [-C C] [-M M] [-A A] [-H]

optional arguments:
  -h, --help     show this help message and exit
  -r PATH_JOBS   path to file with target jobs
  -j JOB         job and city target [job:city]
  -l CREDS       username and password linkedin account [username:password]
  -c PATH_CREDS  path to file with credentials
  -H             run it not headless (show browser)

  -a             apply to jobs sending an email, reqired -M, -C, -A
  -C C           path to file with credentials smp server
  -M M           path to file with email body
  -A A           path to file to attach (Curriculum)

Format for credentials in command line argument or in file:
username:password

Format for target jobs in command line argument or in file (evrey line):
job:city

Format for file smtp credentials:
username:password:server:port
```

For see the results:
```
sqlite3 jobs.db

# All the resutlts
SELECT * FROM offerts;

# Offerts with email associeted
SELECT * FROM offerts WHERE email is not null and email != 'unknown';
```
