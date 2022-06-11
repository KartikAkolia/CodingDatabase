#!/usr/bin/env python3
from smb.SMBConnection import SMBConnection

userID = 'kartikakolia-optiplex-790'
password = 'Kartik84'
client_machine_name = 'kartikakolia-optiplex-790'

server_name = 'kartikakolia-optiplex-790'
server_ip = '192.168.0.102'

domain_name = 'kartikakolia-optiplex-790'

conn = SMBConnection(userID, password, client_machine_name, server_name, domain=domain_name, use_ntlm_v2=True,
                     is_direct_tcp=True)

conn.close()
