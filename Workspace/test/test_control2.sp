*ng_script

.control
	source test.cir
	save out n002 v+ v-
	ac dec 40 1 1G
	wrdata ac all
.endc

.end 