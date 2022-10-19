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
    
        xml_file = Path(r'C:/stc_tests/IPv4_ISIS_4Ports_QoS_dot1Q_TestIQ.xml')
        
        exported_test_xml_file = Path(r'C:/stc_tests/Export_IPv4_ISIS_4Ports_QoS_TestIQ.xml')
    
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
        # helper functions to retrieve results from orion (TestIQ)
        ################################################################################
        ServiceUrl = ''
        query_skeleton = {
            "database": {
                "id": ""
            },
            "mode": "once",
            "definition": {}
        }


        def get_databases_url():
            return ServiceUrl + "/databases"


        def get_header():
            return {
                'Content-Type': 'application/json'
            }


        def get_db_id_url(id):
            return get_databases_url() + "/" + str(id)


        def get_db_write_url(id):
            return get_databases_url() + "/" + str(id) + "/write"


        def get_query_url(id):
            return ServiceUrl + "/queries"


        def get_query_data(query, db_id):
            query_data = copy.deepcopy(query_skeleton)
            query_body = copy.deepcopy(query)
            query_data['database']['id'] = db_id
            query_data['definition'] = query_body
            return query_data


        def do_query(query, db_id):
            response = requests.post(get_query_url(db_id), headers=get_header(), json=get_query_data(query, db_id))
            if response.status_code != 200:
                print('Error perform orion res-request- Get query data, status code: ' + str(response.status_code))
                return {}
            else:
                return response.json()


        ####################################################################
        ## Queries to Orion (from TestIQ WebUI)
        ####################################################################

        query_streamblocks = \
            {
                "multi_result": {
                    "filters": [],
                    "groups": [],
                    "orders": [
                        "view.tx_stream_stream_id ASC",
                        "view.rx_stream_key ASC"
                    ],
                    "projections": [
                        "view.tx_stream_stream_id as tx_stream_stream_id",
                        "view.tx_port_name as tx_port_name",
                        "view.rx_port_name as rx_port_name",
                        "view.stream_block_name as stream_block_name",
                        "view.src_endpoint_name as src_endpoint_name",
                        "view.dst_endpoint_name as dst_endpoint_name",
                        "view.tx_stream_config_ipv4_1_source_addr as tx_stream_config_ipv4_1_source_addr",
                        "view.tx_stream_config_ipv4_1_dest_addr as tx_stream_config_ipv4_1_dest_addr",
                        "view.tx_stream_stats_l1_bit_rate as tx_stream_stats_l1_bit_rate",
                        "view.rx_stream_stats_l1_bit_rate as rx_stream_stats_l1_bit_rate",
                        "view.rx_stream_stats_avg_latency as rx_stream_stats_avg_latency",
                        "view.rx_stream_stats_max_jitter as rx_stream_stats_max_jitter",
                        "view.rx_stream_stats_out_seq_frame_count as rx_stream_stats_out_seq_frame_count",
                        "view.stream_stats_frame_loss_percent as stream_stats_frame_loss_percent"
                    ],
                    "subqueries": [
                        {
                            "alias": "view",
                            "filters": [
                                "rxss.tx_stream_stream_id=txss.tx_stream_stream_id"
                            ],
                            "groups": [],
                            "projections": [
                                "rxss.tx_stream_stream_id as tx_stream_stream_id",
                                "rxss.tx_port_name as tx_port_name",
                                "rxss.rx_port_name as rx_port_name",
                                "rxss.stream_block_name as stream_block_name",
                                "rxss.src_endpoint_name as src_endpoint_name",
                                "rxss.dst_endpoint_name as dst_endpoint_name",
                                "rxss.tx_stream_config_ipv4_1_source_addr as tx_stream_config_ipv4_1_source_addr",
                                "rxss.tx_stream_config_ipv4_1_dest_addr as tx_stream_config_ipv4_1_dest_addr",
                                "txss.l1_bit_rate as tx_stream_stats_l1_bit_rate",
                                "rxss.l1_bit_rate as rx_stream_stats_l1_bit_rate",
                                "rxss.avg_latency as rx_stream_stats_avg_latency",
                                "rxss.max_jitter as rx_stream_stats_max_jitter",
                                "rxss.out_seq_frame_count as rx_stream_stats_out_seq_frame_count",
                                "((100.0 /greatest(1,txss.frame_count)) * (greatest(0, rxss.dropped_frame_count, (txss.frame_count - (rxss.frame_count - greatest(0, rxss.duplicate_frame_count)) - (greatest(txss.frame_rate, rxss.frame_rate) * ( 2 + greatest(0,(txss.counter_timestamp - rxss.counter_timestamp)/40000000))))))) as stream_stats_frame_loss_percent",
                                "rxss.rx_stream_key as rx_stream_key"
                            ],
                            "subqueries": [
                                {
                                    "alias": "rxss",
                                    "filters": [
                                        "rx_stream_live_stats$last.is_deleted = false"
                                    ],
                                    "groups": [],
                                    "projections": [
                                        "stream_block.name as stream_block_name",
                                        "tx_stream.stream_id as tx_stream_stream_id",
                                        "tx_port.name as tx_port_name",
                                        "rx_port.name as rx_port_name",
                                        "(rx_stream_live_stats$last.frame_count) as frame_count",
                                        "src_endpoint.name as src_endpoint_name",
                                        "dst_endpoint.name as dst_endpoint_name",
                                        "tx_stream_config.ipv4_1_source_addr as tx_stream_config_ipv4_1_source_addr",
                                        "tx_stream_config.ipv4_1_dest_addr as tx_stream_config_ipv4_1_dest_addr",
                                        "(rx_stream_live_stats$last.l1_bit_rate) as l1_bit_rate",
                                        "(rx_stream_live_stats$last.total_latency/rx_stream_live_stats$last.frame_count) as avg_latency",
                                        "(rx_stream_live_stats$last.max_jitter) as max_jitter",
                                        "(rx_stream_live_stats$last.out_seq_frame_count) as out_seq_frame_count",
                                        "(rx_stream_live_stats$last.counter_timestamp) as counter_timestamp",
                                        "(rx_stream_live_stats$last.frame_rate) as frame_rate",
                                        "(rx_stream_live_stats$last.dropped_frame_count) as dropped_frame_count",
                                        "(rx_stream_live_stats$last.duplicate_frame_count) as duplicate_frame_count",
                                        "rx_stream.key as rx_stream_key"
                                    ]
                                },
                                {
                                    "alias": "txss",
                                    "filters": [
                                        "tx_stream_live_stats$last.is_deleted = false"
                                    ],
                                    "groups": [],
                                    "projections": [
                                        "stream_block.name as stream_block_name",
                                        "tx_stream.stream_id as tx_stream_stream_id",
                                        "tx_port.name as tx_port_name",
                                        "(tx_stream_live_stats$last.frame_count) as frame_count",
                                        "src_endpoint.name as src_endpoint_name",
                                        "dst_endpoint.name as dst_endpoint_name",
                                        "tx_stream_config.ipv4_1_source_addr as tx_stream_config_ipv4_1_source_addr",
                                        "tx_stream_config.ipv4_1_dest_addr as tx_stream_config_ipv4_1_dest_addr",
                                        "(tx_stream_live_stats$last.l1_bit_rate) as l1_bit_rate",
                                        "(tx_stream_live_stats$last.counter_timestamp) as counter_timestamp",
                                        "(tx_stream_live_stats$last.frame_rate) as frame_rate"
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }

        query_isis = {
            "multi_result": {
                "filters": [],
                "groups": [],
                "orders": [
                    "view.port_name_str_order ASC",
                    "view.port_name_num_order ASC",
                    "view.port_name_ip_order ASC",
                    "view.port_name_hostname_order ASC",
                    "view.port_name_slot_order ASC",
                    "view.port_name_port_num_order ASC",
                    "view.emulated_device_name_str_order ASC",
                    "view.emulated_device_name_num_order ASC"
                ],
                "projections": [
                    "view.port_name as port_name",
                    "view.emulated_device_name as emulated_device_name",
                    "view.state as state",
                    "view.adjacency_three_way_state as adjacency_three_way_state",
                    "view.adjacency_level as adjacency_level",
                    "view.tx_ptp_hello_count as tx_ptp_hello_count",
                    "view.rx_ptp_hello_count as rx_ptp_hello_count",
                    "view.rx_l2_lsp_count as rx_l2_lsp_count",
                    "view.tx_l2_lsp_count as tx_l2_lsp_count"
                ],
                "subqueries": [
                    {
                        "alias": "view",
                        "filters": [
                            "isis_router_live_stats$last.is_deleted = false"
                        ],
                        "groups": [],
                        "orders": [],
                        "projections": [
                            "port.name as port_name",
                            "emulated_device.name as emulated_device_name",
                            "(isis_router_live_stats$last.state) as state",
                            "(isis_router_live_stats$last.adjacency_three_way_state) as adjacency_three_way_state",
                            "(isis_router_live_stats$last.adjacency_level) as adjacency_level",
                            "(isis_router_live_stats$last.tx_ptp_hello_count) as tx_ptp_hello_count",
                            "(isis_router_live_stats$last.rx_ptp_hello_count) as rx_ptp_hello_count",
                            "(isis_router_live_stats$last.rx_l2_lsp_count) as rx_l2_lsp_count",
                            "(isis_router_live_stats$last.tx_l2_lsp_count) as tx_l2_lsp_count",
                            "port.name_str_order as port_name_str_order",
                            "port.name_num_order as port_name_num_order",
                            "port.name_ip_order as port_name_ip_order",
                            "port.name_hostname_order as port_name_hostname_order",
                            "port.name_slot_order as port_name_slot_order",
                            "port.name_port_num_order as port_name_port_num_order",
                            "emulated_device.name_str_order as emulated_device_name_str_order",
                            "emulated_device.name_num_order as emulated_device_name_num_order"
                        ]
                    }
                ]
            }
        }

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

        stc.perform("loadfromxml",filename="IPv4_ISIS_4Ports_QoS_dot1Q_TestIQ.xml")

        xml_object_project = stc.get('project1')

        print ("\nProject1 Object: \n")
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

        ################################################################################
        # Attach ports and bring them online.
        # The currently configured speed child object is automatically created
        ################################################################################

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
        ## Example stc.perform: Retrieve Stream Block Info              ###
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
        
        print ("Project1 Children Objects:\n")

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

        print("\nOptional: Change Device Parameters")
        print("**********************************")

        for ii in xml_device_list:
            devname = stc.get(ii,'Name')
            if 'STCR1' in devname:
                print ("\nSTCR1 Router Detected-> Conf VLAN")
                vlanif = stc.get(ii,'children-vlanif')
                stc.config(vlanif,VlanId=port1_vlan_id)
            elif 'STCR2' in devname:
                print ("\nSTCR2 Router Detected-> Conf VLAN")
                vlanif = stc.get(ii,'children-vlanif')
                stc.config(vlanif,VlanId=port2_vlan_id)
            elif 'STCR3' in devname:
                print ("\nSTCR3 Router Detected-> Conf VLAN")
                vlanif = stc.get(ii,'children-vlanif')
                stc.config(vlanif,VlanId=port3_vlan_id)
            elif 'STCR4' in devname:
                print ("\nSTCR4 Router Detected-> Conf VLAN")
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
                print("\nDefault Detected: 70% Line Rate")
                stc.config(ii,Load='70')
                stc.config(ii,LoadUnit='PERCENT_LINE_RATE')
            elif "VoIP" in strname:
                print("\nVoIP Detected: 20% Line Rate")
                stc.config(ii,Load='20')
                stc.config(ii,LoadUnit='PERCENT_LINE_RATE')
            else:
                print('No Default or  VoIP in the name of the streamblock, so nothing is changed.')

        Get_GC1 = stc.get("generatorconfig1")
        print("\n Generator Config 1")
        pprint.pprint(Get_GC1,width=1)

        #####################################################################
        # Optianlly Change streamblock Parameters:
        # Change streamblock p-bit priority: We need to find the vlan handle.
        # This is a child of vlans, which is a child of ethernet:ethernetii
        #####################################################################

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
        # prepare elements to connect to TCIQ
        ################################################################################
        # get dbID
        test_Info = stc.get('project1', 'children-testinfo')
        dbId = stc.get(test_Info, 'resultdbId')
        # get serviceUrl
        result_Config = stc.get('system1', 'children-TemevaResultsConfig')
        ServiceUrl = stc.get(result_Config, 'ServiceUrl')

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
            print("\nStarting Devices:", xml_device_list)
            # convert the list to a string

            xml_isis_router_config_str = ' '.join([str(elem) for elem in xml_isis_router_config_list])
            stc.perform("ProtocolStart",ProtocolList=xml_isis_router_config_str)
            print ("\n\nProtocolStart: ",xml_isis_router_config_str)

            stc.perform("WaitForRouterStateCommand",ObjectList=xml_isis_router_config_str,WaitRouterState='PROTOCOL_UP',WaitTime="60")
            # for ii in xml_isis_router_config_list:
            # example to check manually if sessions are up (should be UP)
            # print(stc.get(stc.get(ii,'parent'),'Name'), " has blockstate ", stc.get(ii,"BlockState"))
            #  apply to make sure the results of the traffic are visible

            stc.apply()


            ###############################################################################
            # Get ISIS Live Data - TestIQ
            ###############################################################################

            print('---- Query for live isis session result:')
            isis_live = do_query(query_isis, dbId)

            # Res_Live is a dictionary: get columns

            isis_col_name = isis_live['result']['columns']
            print('---- column names:')
            for n in isis_col_name:
                print(n)

            ## get state

            rows = isis_live['result']['rows']
            print('---- total number of rows in result: %d' % (len(rows)))
            for r in rows:
                print("%s state: %s" % (r[1], r[2]))


            ################################################################################
            # resolve arp
            ################################################################################
            print("arp on all streamblocks")
            stc.perform('ArpNdStartOnAllStreamBlocks')

            ################################################################################
            # start traffic - Collect Results - Stop Traffic
            ################################################################################
            # start all traffic everywhere
            stc.perform("GeneratorStart",GeneratorList="project1")

            # Wait for 10 seconds
            time.sleep(10)

            # start traffic on specific port
            #stc.perform("generatorstart",generatorlist=xml_port_list[0])

            # display some counters every 2 seconds while traffic is running
            # print some results from the rxstreamsummary and tx stream results
            i = 5
            while i > 0:
                res_live = do_query(query_streamblocks, dbId)
                # res_live is a dict, get columns
                col_name = res_live['result']['columns']
                print ('---- column names:')
                for n in col_name:
                  print (n)
                # print some results
                rows = res_live['result']['rows']
                for r in rows:
                    print("Streamblock", r[3], " From ", r[4], " To ", r[5], " TX (bps): ",r[8], " RX (bps): ",r[9],\
                          " Avg Lat (us): ",r[10], " Max Jitter(us): ",r[11]," Loss(%): ",r[13])

                time.sleep(2)
                i -= 1
                print("\r")




        ################################################################################
        # clean up
        ################################################################################
        stc.perform("saveasxml",filename=exported_test_xml_file)
        stc.perform("chassisDisconnectAll")
        stc.perform("resetConfig",Config="project1")

        ################################################################################
        # delete session will remove all configuration and free ports
        ################################################################################



        print ("\nAll done....Bye!")
        stc.end_session()








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
    #stc.end_session()
    raise