# jobfinder

This script scarp linkedin jobs offerts with Selenium and write company sites down,
then crowl each sites looking for emails address using regex and write them down.
Optionaly can send mail to apply to the job, must provide credentials for smtp server, body text, and attachement (Curriculum)

The program assume you have firefox and geckodriver installed respectively in /usr/bin/firefox-esr and /usr/local/bin/geckodriver
and you are using a *nix-like system ( if you don't, you should)

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
```
