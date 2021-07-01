*ng_script

.control
	source test.cir
	show r : resistance , c : capacitance > list
	op
	wrdata op all
.endc

.end