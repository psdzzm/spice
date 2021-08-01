*ng_script

.control
	source cmrr.net
	save out
	set wr_vecnames
	let mc_runs = 9
	let run = 0
	set curplot=new          $ create a new plot
	set scratch=$curplot     $ store its name to 'scratch'
	let cutoff=unitvec(mc_runs)
	setseed 1627831314
	
	dowhile run < mc_runs
		alter c1=unif(4.4e-10,0.05)
		alter c2=unif(1e-06,0.05)
		alter c3=unif(4.4e-10,0.05)
		alter c4=unif(1e-06,0.05)
		alter r1=unif(100000,0.01)
		alter r2=unif(100000,0.01)
		alter r3=unif(100000,0.01)
		alter r4=unif(1000,0.01)
		alter r5=unif(1000,0.01)
		
		ac dec 40 100.0 3000.0
		
		meas ac vout find V(out) when frequency=1000
		let {$scratch}.cutoff[run] = db(1/vout)
		destroy $curplot
		let run = run + 1
	end
	
	setplot $scratch
	wrdata fc cutoff
.endc

.end
