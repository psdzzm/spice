*ng_script

.control
	source run.cir
	save out
	ac dec 40 10.0 100.0
	meas ac ymax MAX v(out)
	let v3db = ymax/sqrt(2)
	meas ac cut when v(out)=v3db fall=last
.endc

.end