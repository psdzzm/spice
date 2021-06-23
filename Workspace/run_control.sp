*ng_script

.control
	source run.cir
	save out
	let mc_runs = 100
	let run = 0
	set curplot=new          $ create a new plot
	set scratch=$curplot     $ store its name to 'scratch'
	let cutoff=unitvec(mc_runs)
	setseed 1624464066

	dowhile run < mc_runs
		alter c1=gauss(2e-12,0.05,3)
		alter c2=gauss(7e-13,0.05,3)
		alter r1=gauss(39000,0.01,3)
		ac dec 40 2371374.0 387687500.0

		meas ac ymax MAX v(out)
		let v3db = ymax/sqrt(2)
		meas ac cut when v(out)=v3db fall=last
		let {$scratch}.cutoff[run] = cut
		let run = run + 1
	end

	setplot $scratch
	wrdata fc cutoff
.endc

.end