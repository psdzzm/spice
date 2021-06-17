*ng_script

.control
	source run.cir
	save out
	let mc_runs = 1000
	let run = 0
	set curplot=new          $ create a new plot
	set scratch=$curplot     $ store its name to 'scratch'
	let cutoff=unitvec(mc_runs)
	setseed 1623936513

	dowhile run < mc_runs
		alter c1=gauss(2e-11,0.05,3)
		alter r1=gauss(1000,0.01,3)
		ac dec 40 0.1 51219190.0

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