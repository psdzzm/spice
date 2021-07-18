*ng_script

.control
	set wr_vecnames
	source test.cir
	show r : resistance , c : capacitance > list
	op
	wrdata op all
.endc

.end