*ng_script

.control
    options wr_singlescale
	show r : resistance , c : capacitance > list
    op
	wrdata test all
.endc

.control
    options wr_singlescale
    ac dec 40 1 1G
    wrdata ac vdb(1) vdb(2) vdb(3) vdb(4) vdb(10) vdb(out)
.endc


*ng_script

.control
	source run.cir
	save out
	let mc_runs = 100
	let run = 0
	set curplot=new          $ create a new plot
	set scratch=$curplot     $ store its name to 'scratch'
	let cutoff=unitvec(mc_runs)
	setseed 1625086072

	dowhile run < mc_runs
		alter c1=unif(2e-12,0.05)
		alter c2=unif(7e-13,0.05)
		alter r1=unif(39000,0.01)
		ac dec 40 1000000.0 100000000.0

		meas ac ymax MAX v(out)
		let v3db = ymax/sqrt(2)
		meas ac cut when v(out)=v3db fall=last
		let {$scratch}.cutoff[run] = cut
        print @c1[capacitance] @c2[capacitance] @r1[resistance] >> param
		destroy $curplot
		let run = run + 1
	end

	setplot $scratch
	wrdata fc cutoff
.endc

.end