*ng_script

.control
	source run.cir
	save out
	set wr_vecnames appendwrite
	let mc_runs = 5000
	let run = 0
	set curplot=new          $ create a new plot
	set scratch=$curplot     $ store its name to 'scratch'
	let cutoff=unitvec(mc_runs)
	setseed 1625158535

	dowhile run < mc_runs
		alter c1=unif(2e-12,0.05)
		alter c2=unif(7e-13,0.05)
		alter r1=unif(39000,0.01)
		print @c1[capacitance] @c2[capacitance] @r1[resistance] >> paramlist
		ac dec 40 1000000.0 100000000.0

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
