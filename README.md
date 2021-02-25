If you come here from a job application, probably has been sent by this bot

# jobfinder

This scripts scarp linkedin jobs offert with Selenium and write company sites down,
then crowl each sites looking for emails address by regex and write them down.
Optionaly can send mail to apply to the jobs, must provide credentials for smtp server, body text, and attachement (Curriculum)

Many things can go wrong with linkedin and Selenium, i will try yo keep it updated
If have problem to login, try to run it not headless (-H) possibly linkedin have reconize Selenium and ask for a captcha,
solve it and run it again.


# To Do

- Handle login with request to avoid selenium related problems 

# usage

pip3 install -r requirements.txt
python3 jobfinder.py -h
