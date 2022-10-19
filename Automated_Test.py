import time
import sys
from time import sleep
import requests
import json
import datetime
import copy
import urllib
import pprint
from pathlib import Path, WindowsPath

#Spirent Specific

from StcPython import StcPython
from stcrestclient import stchttp



try:

        ################################################################################
        # Define test parameters
        ################################################################################

        # general test parameters

        chassis_address = "192.168.0.102"

        port1_slot = "1/1"
        port2_slot = "1/2"
        port3_slot = "1/3"
        port4_slot = "1/4"
    
        license_server = "192.168.0.100"
    
        # where to save results
    
        results_dir = Path(r'C:/stc_tests')
    
        # configuration to load
    
        xml_file = Path(r'C:/stc_tests/IPv4_ISIS_4Ports_QoS_dot1Q.xml')
        
        exported_test_xml_file = Path(r'C:/stc_tests/Export_IPv4_ISIS_4Ports_QoS.xml')
    
        # specific test parameters

        port1_vlan_id = "1"
        port2_vlan_id = "1"
        port3_vlan_id = "1"
        port4_vlan_id = "1"
        

        # Sequencers parameters
        # to use sequencer set variable below to 1, oterhwise use 0
    
        useSeq  = "0"
        result_filename = Path(r"c:/stc_tests/scriptFromGUI.db")
    
        ################################################################################
        # Global variables pointing to where the stcweb is running 
        ################################################################################

        global ls_httpPort 
        global lab_server

        # Labserver/StcWeb ports and server to connect directly (stcweb running on linux or windows pc)

        lab_server = '192.168.0.80'
        ls_httpPort = '80'

        # session name and user name of this session, needs to be a unique combination
    
        session_name = 'Session1' 
        username = 'nacho'

        ################################################################################
        #  connect to the stcweb server 
        ################################################################################
        
        stc = stchttp.StcHttp(lab_server + ':' + ls_httpPort,timeout=0)

        ################################################################################
        # Create a new session on server srvip with port srvport and the project
        ################################################################################
        sid = stc.new_session(username,session_name,kill_existing=True)

        # display the  stcweb  version
        sys_info = stc.system_info()
        pprint.pprint(sys_info, width=1)


        ################################################################################
        # Configure license server 
        ################################################################################

        # for virtual, the command below might be necessary to add the licenseserver to the api.  
        # verify wheter the license server already exists, if not add it.
        
        licSrvMgr = stc.get("system1", "children-licenseservermanager")
        if stc.get(licSrvMgr, "children") == "":
        
        # there is not any license server configured, so it can be added
        
            licsrv = stc.create('licenseserver',under=licSrvMgr,server=license_server)
            print(" No license server exists, so the licenseserver ", license_server," is created.")
        else:
            licsrvtlist = stc.get(licSrvMgr,"children")
            licsrvlist = licsrvtlist.split()
            exist = 0
            for ii in licsrvlist:
                if stc.get(ii,"Server") == license_server:
                # licenserver exists already so set exist to 1 and exit loop
                    exist = 1
                    print (" The license server", license_server," exists, so nothing is created.")
                    break
        if exist == 0:
            #licenseserver doesn't exist yet, so needs to be added
            licsrv = stc.create("licenseServer",under=licSrvMgr,server=license_server)
            print(" The specified license server does not exist, so the licenseserver ", license_server," is created.")

        ################################################################################
        #Load configuration from XML file 
        ################################################################################
        
        #upload to labserver
        stc.upload(xml_file)

        #load it into the session

        stc.perform("loadfromxml",filename="IPv4_ISIS_4Ports_QoS_dot1Q.xml")
        print ("\nConfig XML file loaded: ", xml_file)

        xml_object_project = stc.get('project1')
        
        pprint.pprint(xml_object_project, width=1)
        

        ################################################################################
        # Relocate and Attach Ports 
        ################################################################################
        # replace the original ports with the specified ones
        # create a list of the ports from the xmlfile

        xml_port_list = stc.get('project1','children-port').split(' ')

        print("\nList of Ports from XML File\n")
        
        pprint.pprint(xml_port_list, width=1)
        
        # reconfigure the ports to the new location as specified

        print("Relocating ports...")

        port1 = "//%s/%s" %(chassis_address,port1_slot)
        port2 = "//%s/%s" %(chassis_address,port2_slot)
        port3 = "//%s/%s" %(chassis_address,port3_slot)
        port4 = "//%s/%s" %(chassis_address,port4_slot)

        print("Port1 Location = ",port1)
        print("Port2 Location = ",port2)
        print("Port3 Location = ",port3)
        print("Port4 Location = ",port4)
        
        stc.config(xml_port_list[0],Location=port1)
        stc.config(xml_port_list[1],Location=port2)
        stc.config(xml_port_list[2],Location=port3)
        stc.config(xml_port_list[3],Location=port4)

        # Attach ports and bring them online.  the currently configured speed child object is automatically created
        #This section probably needs a watchdog timer or an error handler 

        print("Attaching Ports ...")
        stc.perform("attachPorts",portList=xml_port_list,autoConnect="TRUE",RevokeOwner="TRUE")
        
        
        
        ################################################################################
        # Create lists of handles in case needed later on
        ################################################################################
        
        #Emulated Devices List
        
        xml_device_list = stc.get("project1","children-emulateddevice").split(' ')
        
        print ("Devices List:")
        pprint.pprint (xml_device_list, width=1)

        #Traffic Generators List
        
        xml_port_list = stc.get('project1','children-port').split(' ')
        xml_generator_list = []
        for ii in xml_port_list:
            xml_generator_list.append(stc.get(ii,'children-generator'))

        print ("Generators List:")
        pprint.pprint(xml_generator_list, width=1)

        
        #StreamBlock List
        
        xml_stream_block = ""
        
        for ii in xml_port_list:
            xml_stream_block = xml_stream_block + stc.get(ii,'children-streamblock')
            xml_stream_block = xml_stream_block + ' '

        xml_stream_block= xml_stream_block.rstrip()
        xml_stream_block_list = xml_stream_block.split(' ')

        print("Stream Block List:\n")

        pprint.pprint(xml_stream_block_list, width=1)



        ###################################################################
        ## Example stc.perform: Retrieve Stream Block Info                                   ###
        ###################################################################

        dictStreamBlockInfo = stc.perform("StreamBlockGetInfo", StreamBlock='streamblock1')
        print ("\nStreamBlock 1 Info: \n")
        for szName in dictStreamBlockInfo:
            print ("\t", szName, "\t", dictStreamBlockInfo[szName])
        print ("\n\n")

        ##########################################################
        # Get and Display project children objects               # 
        ##########################################################

        Get_Project = stc.get("project1","children").split(' ')
        
        print ("Project Children Objects:\n")

        pprint.pprint(Get_Project, width=1)

        ########################################################
        # Get and Display children StreamBlockLoadProfile1             #
        ########################################################

        Get_StrBLoad_Profile = stc.get("streamblockloadprofile1")

        print ("\n\nStream Block Load Profile 1 : \n")
        pprint.pprint (Get_StrBLoad_Profile, width=1)

        ########################################################
        # Get and Display children emulateddevice1             #
        ########################################################

        Get_EmDev = stc.get("emulateddevice1")

        print ("\n\nEmulated Device 1: \n")
        pprint.pprint (Get_EmDev, width=1)

        ###########################################################
        # Get Emulated Device 1 children objects                  #
        ###########################################################
        
        Get_ED1_Children = stc.get("emulateddevice1","children").split(' ')
        #children is a list
        print ("\nEmulated Device 1 Children List: \n\n")
        pprint.pprint(Get_ED1_Children, width=1)
        
        ###########################################################
        # Get Emulated Device 1 ISIS Config                  #
        ###########################################################
        
        Get_ISIS_Config = stc.get("isisrouterconfig1")
        #isisrouterconfig1 is a dictionary: no split() method allowed
        print ("\n\nEmulated Device 1 ISIS Config Parameters: \n\n")
        pprint.pprint(Get_ISIS_Config, width=1)

        ##############################################################
        # Get  Project's child Object Port's Childrens
        ##############################################################

        Get_ED = stc.get("project1.port","children")
        print ("project1.port Children")
        pprint.pprint(Get_ED, width=1)

        ################################################################################
        # Optionally change device parameters
        ################################################################################
        # to change specified parameters, like vlanId, ip addresses,...  
        # Do not change  encapsulation or protocols  as this will require the streamblocks
        #  to be removed and recreated
        # In the example the vlanIds are changed, but same principle applies for the other values
        # NO DOT1Q IN MY VMWARE SETUP
        ####################################################################################
        for ii in xml_device_list:
            devname = stc.get(ii,'Name')
            print (devname)
        if 'STCR1' in devname:
            print ("STCR1")
            vlanif = stc.get(ii,'children-vlanif')
            stc.config(vlanif,VlanId=port1_vlan_id)
        elif 'STCR2' in devname:
            print ("STCR2")
            vlanif = stc.get(ii,'children-vlanif')
            stc.config(vlanif,VlanId=port2_vlan_id)
        elif 'STCR3' in devname:
            print ("STCR3")
            vlanif = stc.get(ii,'children-vlanif')
            stc.config(vlanif,VlanId=port3_vlan_id)
        elif 'STCR4' in devname:
            print ("STCR4")
            vlanif = stc.get(ii,'children-vlanif')
            stc.config(vlanif,VlanId=port4_vlan_id)
        else:
            print('No changes done on the devices.')

        stc.apply()

        ################################################################################
        # Optionally change load parameters and streamblock priority
        ################################################################################
        # to change specified parameters, like p-bit/dscp/...
        # It's also possible to add specific additional headers
        # change load to port based/Rate based and actual load  
        # change schedulingmode to RATE_BASED for both ports

        xml_generator_config_list = []
        for ii in xml_generator_list:
            xml_generator_config_list.append(stc.get(ii,'children-generatorconfig'))
            print (xml_generator_config_list)

        for ii in xml_generator_config_list:
            stc.config(ii,SchedulingMode='RATE_BASED')

        # Change streamblock loadmode and loadUnit
        # PERCENT_LINE_RATE Specify load as a percent of the port line rate.
        # FRAMES_PER_SECOND Specify load as frames per second.
        # INTER_BURST_GAP Specify load by inter-burst gap.
        # MEGABITS_PER_SECOND Specify load in megabits per second.
        # KILOBITS_PER_SECOND Specify load in kilobits per second.
        # BITS_PER_SECOND Specify load in bits per second.

        for ii in xml_stream_block_list:
            strname = stc.get(ii,'Name')
            print (strname)
            if "Default" in strname:
                print("\nDefault Detected")
                stc.config(ii,Load='70')
                stc.config(ii,LoadUnit='PERCENT_LINE_RATE')
            elif "VoIP" in strname:
                print("\nVoIP Detected")
                stc.config(ii,Load='20')
                stc.config(ii,LoadUnit='PERCENT_LINE_RATE')
            else:
                print('No Default or  VoIP in the name of the streamblock, so nothing is changed.')

        Get_GC1 = stc.get("generatorconfig1")
        print("\n Generator Config 1")
        pprint.pprint(Get_GC1,width=1)

        # Change streamblock p-bit priority
        # We need to find the vlan handle.
        # This is a child of vlans, which is a child of ethernet:ethernetii

        for ii in xml_stream_block_list:
            stc.config(ii,ShowAllHeaders='TRUE')
        stc.apply()

        for ii in xml_stream_block_list:
            ethh = stc.get(ii,'children-ethernet:ethernetii')
            vlansh = stc.get(ethh,'children-vlans')
            vlanh = stc.get(vlansh,'children-vlan')
            strname = stc.get(ii,'Name')
        
        if "Default" in strname:
            stc.config(vlanh,pri='000')
        elif "VoIP" in strname:
            stc.config(vlanh,pri='110')
        else:
            print('No Default or VoIP in the name of the streamblock, so no vlan priority is changed.')

        stc.apply()

        ################################################################################
        # select to use sequencer or not
        ################################################################################

        print("configure the correct absolute resultsdirectory")
        testresultsetting = stc.get("project1","children-testresultsetting")
        stc.config (testresultsetting,SaveResultsRelativeTo="NONE",ResultsDirectory=results_dir)

        if useSeq == "1":
        
            # use the built in sequencer and save resultdatabase, 
            # verify it's pointing to the correct directory to save the db file
            
            seq = stc.get("system1","children-sequencer")
            i = 0
            seqchild = stc.get(seq,"children")
            seqchildlist = seqchild.split()
            for ii in seqchildlist:
                if "saveresultscommand1" in ii:
                    stc.config(ii,ResultFileName=result_filename)
            stc.apply()
            stc.perform("sequencerstart")
            while stc.get(seq,"TestState") == "NONE":
                time.sleep(2)
                print("sequencer is executing command ", stc.get(seq,"currentcommand"))
            if stc.get(seq,"TestState") == "PASSED":
                print( "sequencer finished successfully")
            else:
                print("sequencer failed")
        else:        
            #########################################################################################
            ##          RUN TEST MANUALLY
            ##########################################################################################
            ################################################################################
            # subscribe results
            ################################################################################
            print("configure the correct absolute resultsdirectory")
        
            testresultsetting = stc.get("project1","children-testresultsetting")
            stc.config (testresultsetting,SaveResultsRelativeTo="NONE",ResultsDirectory=results_dir)
            
            print("Subscribe to results at port level")
            
            stc.perform('resultssubscribe',Parent="project1",ConfigType="Analyzer",resulttype="AnalyzerPortResults",filenameprefix="AnalyzerPortResults")
            stc.perform('resultssubscribe',Parent="project1",ConfigType="Generator",resulttype="GeneratorPortResults",filenameprefix="GeneratorPortResults")
            
            print("subscribe to results at streamblock level")
            
            stc.perform('resultssubscribe',Parent="project1",ConfigType="StreamBlock",ResultType="TxStreamBlockResults",FilenamePrefix="TxStreamBlockResults",Interval="2")
            stc.perform('resultssubscribe',Parent="project1",ConfigType="StreamBlock",ResultType="TxStreamResults",FilenamePrefix="TxStreamResults",Interval="2")
            stc.perform('resultssubscribe',Parent="project1",ConfigType="StreamBlock",ResultType="RxStreamBlockResults",FilenamePrefix="RxStreamBlockResults",Interval="2")
            stc.perform('resultssubscribe',Parent="project1",ConfigType="StreamBlock",ResultType="RxStreamSummaryResults",FilenamePrefix="RxStreamSummaryResults",Interval="2")
            
            # subscribe ISIS results
            print("subscribe to results at ISIS level")
            stc.perform('resultssubscribe',Parent="project1",resulttype="IsisRouterResults",ConfigType="IsisRouterConfig")
            
            ################################################################################
            # apply configuration
            ################################################################################
            print("Apply configuration")
            stc.apply()
            
            ################################################################################
            # start devices
            ################################################################################
            
            # create some lists of handles can be used later on, 
            # do it at this location so it's done only once in the script
            
            xml_isis_router_config_list = []
            for ii in xml_device_list:
                devname = stc.get(ii,'Name')
                if 'STCR' in devname:
                    xml_isis_router_config_list.append(stc.get(ii,'children-isisrouterconfig'))
                else:
                    print('No STCR string present in the devicename, so ntohing stored in the list.')
            
            # start all protocols on server device

            stc.perform("DeviceStart",DeviceList=xml_device_list)
            # wait until all are bound
            print(xml_device_list)
            # convert the list to a string

            xml_isis_router_config_str = ' '.join([str(elem) for elem in xml_isis_router_config_list])
            stc.perform("ProtocolStart",ProtocolList=xml_isis_router_config_str)
           
            print (xml_isis_router_config_str)

            stc.perform("WaitForRouterStateCommand",ObjectList=xml_isis_router_config_str,WaitRouterState='PROTOCOL_UP',WaitTime="60")
    #        for ii in xml_isis_router_config_list:
    #            # example to check manually if sessions are up (should be UP)
    #            print(stc.get(stc.get(ii,'parent'),'Name'), " has blockstate ", stc.get(ii,"BlockState"))
    #        # apply to make sure the results of the traffic are visible
            stc.apply()

            ################################################################################
            # resolve arp
            ################################################################################

            print("arp on all streamblocks")
            stc.perform('ArpNdStartOnAllStreamBlocks')
            #print("arp on all deviceblocks")
            #stc.perform('ArpNdStartOnAllDevices')

            ################################################################################
            # start/Stop traffic - Collect Results
            ################################################################################

            # start all traffic everywhere
            # stc.perform("GeneratorStart",GeneratorList="project1")

            # start traffic on specific port
            stc.perform("generatorstart",generatorlist=xml_port_list[0])

            # start traffic on specified streamblocks of port2

            xmlstreamblockstr = ' '.join([str(elem) for elem in xml_stream_block_list])
            stc.perform("streamblockstart",streamblocklist=xmlstreamblockstr)
            time.sleep(5)

            # display some counters every 2 seconds while traffic is running
            # print some results from the rxstreamsummary and tx stream results

            i = 5
            while i > 0:
                rxresultlist = []
                txresultlist = []
                for ii in xml_stream_block_list:
                    txresultnolist = stc.get(ii,'children-txstreamresults')
                    txresultlist = txresultlist + txresultnolist.split(' ')
                    rxresultnolist = stc.get(ii,'children-rxstreamsummaryresults')
                    rxresultlist = rxresultlist + rxresultnolist.split(' ')
                time.sleep(2)
                for ii  in txresultlist:
                    for jj in rxresultlist:
                        if stc.get(ii,"StreamId") == stc.get(jj,"Comp32"):
                            print("stream", stc.get(stc.get(ii,"parent"),'Name'), "(streamid ", stc.get(ii,"StreamId"), " send ", stc.get(ii,"FrameRate") ," fps and received ", stc.get(jj,"FrameRate"), " fps with short term average latency ", stc.get(jj,"ShortTermAvgLatency"), " us")
                            print("stream", stc.get(stc.get(ii,"parent"),'Name'), "(streamid ", stc.get(ii,"StreamId"), " send ", stc.get(ii,"framecount")," packets and received ", stc.get(jj,"framecount"), " packets with average latency ", stc.get(jj,"AvgLatency"), " us")
                i -= 1
                print("\r")
            time.sleep(5)
            for ii in xml_port_list:
                stc.perform("GeneratorStop",GeneratorList=stc.get(ii,"children-generator"))
            print("Generator stopped")
            time.sleep(2)

            # Display some statistics.

            for ii in xml_port_list:
                generator = stc.get(ii,"children-Generator")
                GeneratorResults = stc.get(generator,"children-GeneratorPortResults")
                analyzer = stc.get(ii,"children-Analyzer")
                AnalyzerResults = stc.get(analyzer,"children-AnalyzerPortResults")
                print("PortResults ", ii , " Tx Sig frames: ", stc.get(GeneratorResults,"generatorSigFrameCount"))
                print("PortResults ", ii , " Rx Sig frames: ", stc.get(AnalyzerResults,"sigFrameCount"))

            # print some results from the rxstreamblock and txstreamblock results

            txblockresultlist = []
            rxblockresultlist = []
            for ii in xml_stream_block_list:
                txblockresultnolist = stc.get(ii,'children-txstreamblockresults')
                txblockresultlist = txblockresultlist + txblockresultnolist.split(' ')
                rxblockresultnolist = stc.get(ii,'children-rxstreamblockresults')
                rxblockresultlist = rxblockresultlist + rxblockresultnolist.split(' ')
            time.sleep(2)
            for ii in txblockresultlist:
                reschildnolist = stc.get(ii,'resultchild-sources')
                reschildlist = reschildnolist.split(' ')
                for hresdataset in reschildlist:
                    stc.perform("refreshresultview",ResultDataSet=hresdataset)
            for ii in rxblockresultlist:
                reschildnolist = stc.get(ii,'resultchild-sources')
                reschildlist = reschildnolist.split(' ')
                for hresdataset in reschildlist:
                    stc.perform("refreshresultview",ResultDataSet=hresdataset)
            for ii in txblockresultlist:
                for jj in rxblockresultlist:
                    if stc.get(ii,"parent") == stc.get(jj,"parent"):
                        print("streamblock ", stc.get(stc.get(ii,"parent"),'Name') ," send ", stc.get(ii,"framecount") ," packets and received ", stc.get(jj,"framecount") ," packets with average latency ", stc.get(jj,"AvgLatency") ," us")

        ################################################################################
        # clean up
        ################################################################################

        stc.perform("saveasxml",filename=exported_test_xml_file)
        stc.perform("chassisDisconnectAll")
        stc.perform("resetConfig",Config="project1")

        ################################################################################
        # delete session will remove all configuration and free ports
        ################################################################################

        stc.end_session()
        print ("\n\n**************************************")
        print("Test Ended, Session Released....See You!")
        print ("******************************************")


except OSError as err:
    print("OS error: {0}".format(err))
    #stc.end_session()

except RuntimeError as err:
    print("Runtime Error: {0}".format(err))
    stc.end_session(end_tcsession='kill')

except TypeError as err:
    print("Type Error: {0}".format(err))
    stc.end_session(end_tcsession='kill')

except TypeError as e:
    print("Unexpected error:", sys.exc_info()[0])
    stc.end_session()
    raise