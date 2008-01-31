'''
yahooSiteExplorer.py

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

import core.controllers.outputManager as om
from core.controllers.w3afException import w3afException
from core.controllers.w3afException import w3afRunOnce
from core.data.searchEngines.yahooSiteExplorer import yahooSiteExplorer as yse
from core.controllers.basePlugin.baseDiscoveryPlugin import baseDiscoveryPlugin
import core.data.parsers.urlParser as urlParser


class yahooSiteExplorer(baseDiscoveryPlugin):
    '''
    Search Yahoo's index using Yahoo site explorer to get a list of URLs
    @author: Andres Riancho ( andres.riancho@gmail.com )
    '''
    def __init__(self):
        baseDiscoveryPlugin.__init__(self)
        self._run = True
        self._resultLimit = 300
        
    def discover(self, fuzzableRequest ):
        '''
        @parameter fuzzableRequest: A fuzzableRequest instance that contains (among other things) the URL to test.
        '''
        newUrls = []
        self._fuzzableRequests = []
        if not self._run:
            # This will remove the plugin from the discovery plugins to be runned.
            raise w3afRunOnce()
        else:
            # I will only run this one time. All calls to yahooSiteExplorer return the same url's
            self._run = False
            self._yse = yse( self._urlOpener )
            
            domain = urlParser.getDomain( fuzzableRequest.getURL() )
            if self._yse.isPrivate( domain ):
                raise w3afException('There is no point in searching yahoo site explorer for site:'+ domain + '" . Yahoo doesnt index private pages.')

            results = self._yse.getNResults( domain, self._resultLimit )
                
            for res in results:
                targs = (res.URL,)
                self._tm.startFunction( target=self._generateFuzzableRequests, args=targs, ownerObj=self )          
            self._tm.join( self )
        return self._fuzzableRequests
    
    def _generateFuzzableRequests( self, url ):
        try:
            response = self._urlOpener.GET( url, useCache=True, getSize=True )
        except KeyboardInterrupt, k:
            raise k
        except w3afException, w3:
            pass
        except URLError, ue:
            om.out.debug('URL Error while fetching page in yahooSiteExplorer, error: ' + str(ue) )
        else:
            fuzzReqs = self._createFuzzableRequests( response )
            self._fuzzableRequests.extend( fuzzReqs )
    
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
            <Option name="resultLimit">\
                <default>'+str(self._resultLimit)+'</default>\
                <desc>Fetch the first "resultLimit" results from the Google search</desc>\
                <type>integer</type>\
                <help></help>\
            </Option>\
        </OptionList>\
        '

    def setOptions( self, optionsMap ):
        '''
        This method sets all the options that are configured using the user interface 
        generated by the framework using the result of getOptionsXML().
        
        @parameter OptionList: A dictionary with the options for the plugin.
        @return: No value is returned.
        ''' 
        self._resultLimit = optionsMap['resultLimit']

    def getPluginDeps( self ):
        '''
        @return: A list with the names of the plugins that should be runned before the
        current one.
        '''
        return []
    
    def getLongDesc( self ):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin finds new URL's using yaho site explorer. It will search for "domain.com" and do GET requests
        all the URL's found in the result.
        
        One configurable parameters exists:
            - resultLimit
        '''
