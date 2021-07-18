*ng_script

.control
	source run.cir
	save out
	set wr_vecnames
	let run = 0
	set curplot=new          $ create a new plot
	set scratch=$curplot     $ store its name to 'scratch'
	compose x start=11200 stop=12000 step=60
	let cutoff=unitvec(length(x))

	dowhile run < length(x)
		alter r2=x[run]
		ac dec 40 10.0 1000.0

		meas ac ymax MAX v(out)
		let v3db = ymax/sqrt(2)
		meas ac cut when v(out)=v3db fall=last
		let {$scratch}.cutoff[run] = cut
		destroy $curplot
		let run = run + 1
	end

	setplot $scratch
	wrdata fc cutoff
.endc

.end