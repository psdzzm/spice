*ng_script

.control
	set wr_vecnames
	source test.cir
	save out 1 10 2 3 4
	ac dec 40 1 1G
	wrdata ac all
.endc

.end 