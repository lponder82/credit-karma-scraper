#!/usr/bin/env python
"""
This script will log in to creditkarma.com and parse out your credit scores.

usage:
    $ python main.py -u [username] -p [password]

"""

import urllib
import requests
import argparse

from bs4 import BeautifulSoup


def _login_form_data(response):
    """
    Parses out the login form inputs needed for the post request body.

    :param response: response object which contains the form element.
    :return: dict containing input name:value
    """
    soup = BeautifulSoup(response.content, 'html.parser')
    form = soup.find('form', {'id': 'logonform'})
    inputs = {field.get('name'): field.get('value') for field in form.find_all('input') if field.has_attr('name') and field.has_attr('value')}
    inputs.pop('rememberEmail')  # remove remember email field.
    return inputs


def _has_errors(response):
    """
    Check response for an error message.

    Searches for <div ck-message="negative"> and gets the bolded text.
    :param response:
    :return:
    """
    soup = BeautifulSoup(response.content, 'html.parser')
    err_msg = soup.find('div', {'ck-message': 'negative'})
    if err_msg:
        bolded_text = err_msg.find('b')
        if bolded_text:
            return bolded_text.text.strip()


def login(session, username, password):
    """
    Post login for creditkarma.

    :param session: requests.Session object.
    :param username: creditkarma.com username/email
    :param password: creditkarma.com password
    :return:
    """
    print 'fetching index...'
    login_page = session.get('https://www.creditkarma.com')  # get any necessary cookies
    
    # Get the login form modal.
    print 'fetching login form...'
    login_form_response = session.get('https://www.creditkarma.com/auth/logon?modal=1&interstitial=1')
    
    payload = _login_form_data(login_form_response)
    payload.update({'username': username, 'password': password})
    payload = urllib.urlencode(payload)

    url = 'https://www.creditkarma.com/auth/logon'

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # Post login
    print 'logging in...'
    _validator = session.post(url, data=payload, headers=headers)
    errs = _has_errors(_validator)
    if errs:
        raise ValueError(errs)
    
    # Fetch dashboard
    print 'fetching information...'
    return session.get('https://www.creditkarma.com/dashboard')


def parse_scores(response):
    """
    Parse the users credit scores and return a dictionary for each bureau
    :param response:
    :return:
    """
    soup = BeautifulSoup(response.content, 'html.parser')
    scores = soup.find_all('span', {'class': 'score-block'})
    data = dict(
        scores=dict(),
        last_update=''
    )
    for score in scores:
        score_hyperlink = score.a.get('href')
        score_value = int(score.find('span', {'class': 'score-value'}).text.strip())
        score_category = score.find('span', {'class': 'score-rating'}).text.strip()
        for bureau in ['transunion', 'equifax']:
            if bureau in score_hyperlink:
                data['scores'][bureau] = dict(
                    href=score_hyperlink,
                    value=score_value,
                    category=score_category
                )
    dates = soup.find('div', {'class': 'user-score-dates'})
    dates = ' - '.join((x.text.strip() for x in dates.find_all('span')))
    data['last_update'] = dates
    return data


def main(username, password, session=None):
    """
    Login to credit karma and parse out your credit scores.

    Use this method to run the script when imported.

    :param username: creditkarma.com username/email
    :param password: creditkarma.com password
    :param session: requests.Session object
    :return: dict containing scores for each bureau and the last update/next update time
    """
    session = session or requests.Session()
    login_response = login(session, username, password)
    scores = parse_scores(login_response)
    return scores


if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('-p', '--password', help='password for creditkarma', dest='password')
    psr.add_argument('-u', '--username', help='username or email for creditkarma', dest='username')
    args = psr.parse_args()

    sc = main(args.username, args.password)
    for k, v in sc['scores'].items():
        print "{}: {} - {}".format(k, v['value'], v['category'])
    print sc['last_update']
