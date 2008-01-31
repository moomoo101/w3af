'''
targetSettings.py

Copyright 2006 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''

from core.controllers.configurable import configurable
import core.data.kb.config as cf
from core.controllers.misc.parseOptions import parseOptions
import core.data.parsers.urlParser as urlParser
from core.controllers.w3afException import w3afException

cf.cf.save('targets', [] )
cf.cf.save('targetDomains', [] )
cf.cf.save('baseURLs', [] )

class targetSettings(configurable):
    '''
    A class that acts as an interface for the user interfaces, so they can configure the target
    settings using getOptionsXML and SetOptions.
    '''
    
    def __init__( self ):
        # User configured variables
        if cf.cf.getData('targets') == None:
            # It's the first time I'm runned
            # Set the defaults in the config
            cf.cf.save('targets', [] )
            cf.cf.save('targetDomains', [] )
            cf.cf.save('baseURLs', [] )

        
    def getOptionsXML(self):
        '''
        This method returns a XML containing the Options that the plugin has.
        Using this XML the framework will build a window, a menu, or some other input method to retrieve
        the info from the user. The XML has to validate against the xml schema file located at :
        w3af/core/ui/userInterface.dtd
        
        @return: XML with the plugin options.
        ''' 
        return  '<?xml version="1.0" encoding="ISO-8859-1"?>\
        <OptionList>\
            <Option name="target" required="true">\
                <default>'+','.join(cf.cf.getData('targets'))+'</default>\
                <desc>A comma separated list of URLs</desc>\
                <type>list</type>\
            </Option>\
        </OptionList>\
        '
        
    def setOptions( self, optionsMap ):
        '''
        This method sets all the options that are configured using the user interface 
        generated by the framework using the result of getOptionsXML().
        
        @parameter optionsMap: A dictionary with the options for the plugin.
        @return: No value is returned.
        ''' 
        f00, optionsMap = parseOptions( 'targetSettings', optionsMap )
        
        targetUrls = optionsMap['target']
        
        for targetUrl in targetUrls:
            if not targetUrl.count('file://') and not targetUrl.count('http://')\
            and not targetUrl.count('https://'):
                raise w3afException('Invalid format for target URL: '+ targetUrl )
        
        for targetUrl in targetUrls:
            if targetUrl.count('file://'):
                try:
                    f = open( targetUrl.replace( 'file://' , '' ) )
                except:
                    raise w3afException('Cannot open target file: ' + targetUrl.replace( 'file://' , '' ) )
                else:
                    for line in f:
                        targetUrls.append( line.strip() )
                    f.close()
                targetUrls.remove( targetUrl )
        
        # Save in the config, the target URLs, this may be usefull for some plugins.
        cf.cf.save('targets', targetUrls)
        cf.cf.save('targetDomains', [ urlParser.getDomain( i ) for i in targetUrls ] )
        cf.cf.save('baseURLs', [ urlParser.baseUrl( i ) for i in targetUrls ] )

    def getName( self ):
        return 'targetSettings'
        
    def getDesc( self ):
        return 'Configure target URLs'
