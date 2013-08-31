#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2013-03-19

@author: Martin H. Bramwell
'''

import os
import json
import argparse
import errno

args_file = './arguments.json'
credential_file = '.persargs.json'
credential_path = os.path.expanduser('~') + '/' + credential_file
allow_to_overwrite_prior_credentials = True

NONE = -1
SHORT = NONE + 1
LONG = SHORT + 1
HELP = LONG + 1
REQUIRED = HELP + 1
DEFAULT = REQUIRED + 1

'''
arguments = {}
arguments['description'] = 'Helper to initialize Google uid/pwd logins'
arguments['switches'] = [["u", "--user_id", "Name of the connecting user."], ["p", "--user_pwd", "Password of the connecting user."], ["r", "--start_row", "Row in Tasks sheet at which to start processing ."]]
arguments['positional'] = {'val': 'key', 'help': 'A Google Spreadsheet key'}
'''

class InputError(Exception):
    """ Exception raised for errors in the input.
    Attributes:
        expr -- input expression in which the error occurred
        msg -- explanation of the error
    """
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg


def init(credentialFile):
    credential_path = credentialFile

def getArguments():

    arguments = None
    try:
        with open(args_file, 'rb') as fileArguments:
            arguments = json.load(fileArguments)
    except IOError:
    
        import sys
        
        msg  = '\n * * * Warning: Found no arguments meta file. * * * '
        msg += '\n\nCommand line arguments are defined in a JSON file like this :  '
        msg += '\n{'
        msg += '\n   "description": "Helper to initialize Google uid/pwd logins"'
        msg += '\n , "positional": {"help": "A Google Spreadsheet key", "val": "key"}'
        msg += '\n , "switches":' 
        msg += '\n   ['
        msg += '\n       ["u", "--user_id", "Name of the connecting user."]'
        msg += '\n     , ["p", "--user_pwd", "Password of the connecting user."]'
        msg += '\n     , ["r", "--start_row", "Row in Tasks sheet at which to start processing ."]'
        msg += '\n   ]'
        msg += '\n}\n\n\n'

        sys.exit(msg)
        
        exit
        
    return arguments

def dumpArguments(arguments):

    with open(args_file, 'wb') as fileArguments:
        json.dump(arguments, fileArguments)

def load():

    creds = None
    try:
        with open(credential_path, 'rb') as fileCredentials:
            creds = json.load(fileCredentials)
    except IOError:
        print "Found no credentials file : '" + credential_path + "'.  Creating one now ..."

    return creds

def save(creds):

    with open(credential_path, 'wb') as fileCredentials:
        json.dump(creds, fileCredentials)
        
    os.chmod(credential_path, 0600)

    return

def get():

    global allow_to_overwrite_prior_credentials
    
#     dumpArguments(arguments)
    arguments = getArguments()
    
    switch_defaults = {}
    
    parser = argparse.ArgumentParser(description=arguments['description'])

    for switch in arguments['switches']:
        required = switch[REQUIRED] == 'Required'
        default = None if switch[DEFAULT] == 'None' else switch[DEFAULT]
        switch_defaults[switch[LONG]] = default
        parser.add_argument(
                      '-' + switch[SHORT]
                    , '--' + switch[LONG]
                    , dest = switch[LONG]
                    , help = switch[HELP] + '(' + switch[REQUIRED] + '. Default : ' + switch[DEFAULT] + ')'
                    , required = required
                    , default = default)
    

    parser.add_argument(arguments['positional']['val'], help = arguments['positional']['help'])
    args = parser.parse_args()

    alterations = []
    for switch, argument in vars(args).items() :
        if switch in switch_defaults :
            if argument is not None:
                if switch_defaults[switch] != argument :
                    alterations.append(switch)
                    print 'Alteration ==> {} ({})'.format(switch, argument) 
    
    credentials = load()
    if credentials is None:
        credentials = vars(args)
        save(credentials)
    elif len(alterations) > 0:
        answer = {
                  '1':'Overwrote prior credentials.'
                , '2':'Using provided command line options without saving.'
                , '3':'Ignoring command line options and using stored ones.'}
        print 'Prior credentials were found in : ' + credential_path
        print '1) Overwrite prior credentials?'
        print '2) Use provided credentials just this time?'
        print '3) Ignore provided credentials?'
        choice = ' (1/2/3)  '
        inp = raw_input(choice)
        while inp not in ('1', '2', '3') :
            print 'invalid input'
            inp = raw_input(choice)
        print answer[inp]
        allow_to_overwrite_prior_credentials = True
        if (inp != '3'):
            credentials = vars(args)
            if (inp != '2'):
                save(credentials)
            else:
                allow_to_overwrite_prior_credentials = False
    
    return credentials


def silentremove(filename):
    
    if allow_to_overwrite_prior_credentials:
        try:
            os.remove(filename)
        except OSError, e:
            if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
                raise # re-raise exception if a different error occured



