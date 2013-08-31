#!/usr/bin/env python 
# -*- coding: utf-8 -*-
'''

   The full program is explained in the attached ReadMe.md

    Copyright (C) 2013 warehouseman.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Created on 2013-03-19

    @author: Martin H. Bramwell

    This module:
       This module is the main entry point for running the gOAuth generic client to Google document APIs.

'''

import creds

import argparse
import gdata.gauth
import gdata.spreadsheets.client
import urllib, urllib2
import json
import time

import sys
import logging

connection = None

data = {}
data['grant_type'] = 'refresh_token'

maxTries = 4


def refreshToken(credentials):

    logging.debug('Current access token : {}.'.format(credentials['Access_token']))

    data['client_secret'] = credentials['Client_secret']
    data['refresh_token'] = credentials['Refresh_token']
    data['client_id'] = credentials['Client_Id']
    
    request = urllib2.Request (
              "https://accounts.google.com/o/oauth2/token"
            , urllib.urlencode(data)
        )
        
    credentials['Access_token'] = json.loads(urllib2.urlopen(request).read())['access_token']
    logging.debug('Refreshed access token : {}.'.format(credentials['Access_token']))

    return credentials



def getGDataTokens(Client_id, Client_secret, Redirect_URI) :

    Scope='https://spreadsheets.google.com/feeds/'
    User_agent='myself'

    token = gdata.gauth.OAuth2Token(client_id=Client_id,client_secret=Client_secret,scope=Scope,user_agent=User_agent)
    
    print "\n\n* * * * *  You have to verify that you DO allow this software to open your Google document space  * * * * * "
    print "\n\n* * * * *        Here's the URL at which you can pick up your 'one-time' verification code.       * * * * * "
    print token.generate_authorize_url(redirect_uri=Redirect_URI)
    code = raw_input('\nPaste that code here, now . . , then hit <Enter> ').strip()
    
    try :
        token.get_access_token(code)
        
    except :
        if 'n' == raw_input('\nDo you want to try again? (y/n) <Enter> ').strip() :
            exit()
            
        else :
            return None
    
    return token


def getSpreadsheetAPIProxy(access_token) :

    client_id = ''
    client_secret = ''
    scope = ''
    user_agent = ''
    refresh_token = ''

    token = gdata.gauth.OAuth2Token(
          client_id = client_id
        , client_secret = client_secret
        , scope = scope
        , user_agent = user_agent
        , access_token = access_token
        , refresh_token = refresh_token
    )
    
    proxy = gdata.spreadsheets.client.SpreadsheetsClient()
    token.authorize(proxy)
    
    return proxy


def connect(credentials):
    
    gc = {}
    
    gc['workbook_key'] = credentials['Document_key']
    gc['connected'] = False
    
    tries = maxTries

    while not gc['connected'] and tries > 0:
    
        tries -= 1;
        
        if 'Access_token' in credentials and credentials['Access_token'] is not None :
            gc['connection'] = getSpreadsheetAPIProxy(credentials['Access_token'])
            logging.info('Connected.  Testing for token expiry.')
            try :
                if gc['workbook_key'] in str(gc['connection'].get_worksheets(gc['workbook_key']).entry[0]):
                    
                    gc['connected'] = True
                    
            except :
            
                print 'Connected . . . refreshing token.'
                if tries < (maxTries - 1) :
                    print 'Delaying before attempt #{}'.format(maxTries-tries)
                    time.sleep(15)

                refreshToken(credentials)
                creds.save(credentials)
        
        elif 'Client_Id' in credentials and credentials['Client_Id'] is not None :
            if 'Client_secret' in credentials and  credentials['Client_secret'] is not None :
                authorization = getGDataTokens(credentials['Client_Id'], credentials['Client_secret'], credentials['Redirect_URI'])
                if authorization is not None :
                    logging.info('Got a token -- {}. Now try to connect.'.format(authorization.access_token))
                    credentials['Access_token'] = authorization.access_token
                    credentials['Refresh_token'] = authorization.refresh_token
                    creds.save(credentials)
                    
                    
            else:
                sys.exit('Google connection : \n' + 'No client secret was supplied.  Use -s or --Client_secret')
        else:
            sys.exit('Google connection : \n' + 'No Google client ID was supplied.  Use -i or --Client_Id')
        
    return gc
           

def main():

    logging.basicConfig(filename='./log/gOAuth.log',level=logging.DEBUG)
    
    credentials = creds.get()
    for key, cred in credentials.items() :
        if cred is None:
            cred = ''
        if key in {'Client_secret', 'Refresh_token'} :
            cred = cred[0:12].ljust(len(cred), 'x')
        logging.debug('Key : {} has {}.'.format(key, cred))

    google_connection = connect(credentials)
    
    
    logging.info('Connection result {}'.format( google_connection ))
    if google_connection['connected'] :
        msg = 'Authorized.'
        print msg
        logging.info(msg)

    print ''

if __name__ == '__main__':

    main()
	

	
