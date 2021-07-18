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
		ac dec 40 10.0 100.0

		meas ac ymax MAX vdb(out)
		meas ac ymin MIN vdb(out)
		let {$scratch}.cutoff[run] = ymax-ymin
		destroy $curplot
		let run = run + 1
	end

	setplot $scratch
	wrdata fc cutoff
.endc
.end
