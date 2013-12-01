# -*- coding: utf-8 -*-


def decode_address(address):
	""" this function converts address in CoDeSys style to Modbus address
	if the address is already a valid modbus address return this, if not convert
	WAGO        		Modbus      	Access
	%IW0 	- %IW255 	0 		- 255	PLC r / Modbus r
	%ID0	- %ID127	0		- 127	PLC r / Modbus r
	%QW256 	- %QW511    256 	- 511	PLC w / Modbus r
	%QD128  - %QD255	256		- 511	PLC w / Modbus r
	%QW0 	- %QW255    512 	- 767	PLC w / Modbus r
	%QD0	- %QD127	512		- 767	PLC w / Modbus r
	%ID128 	- %ID255 	768 	- 1023	PLC r / Modbus w
	%ID256 	- %ID511 	768 	- 1023	PLC r / Modbus w
	%MW0 	- %MW12287 	12288 	- 24575	PLC rw / Modbus rw
	%MD0 	- %MD6143 	12288 	- 24575	PLC rw / Modbus rw
	"""
	if address[1:2] == 'X':
		address_bits = int(address[address.find('.')+1::])
		address = address[0:address.find('.')]
	if address[0:1] == 'I':
		ModAddress = int(address[2::])
		if address[1:2] == 'D': ModAddress = ModAddress*2
		if (ModAddress < 0 or ModAddress > 511): ModAddress = -1
		if (ModAddress > 255): ModAddress = ModAddress+512
	elif address[0:1] == 'Q':
		ModAddress = int(address[2::])
		if address[1:2] == 'D': ModAddress = ModAddress*2
		if (ModAddress < 0 or ModAddress > 511): ModAddress = -1
		if (ModAddress < 256): ModAddress = ModAddress+512
	elif address[0:1] == 'M':
		ModAddress = int(address[2::])
		if address[1:2] == 'D': ModAddress = ModAddress*2
		ModAddress = ModAddress+12288
		if (ModAddress < 12288 or ModAddress > 24575): ModAddress = -1
	else:
		ModAddress = int(address)
		if (ModAddress < 0 or ModAddress > 24575): ModAddress = -1
	if address[1:2] == 'X':
		ModAddress = [ModAddress,address_bits]
	return ModAddress


def prepare_input_config(controller_id):
	"""

	"""
	variable_config = {}

	return variable_config
