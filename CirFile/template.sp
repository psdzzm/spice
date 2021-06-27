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


.control
    source LPF.cir
    save out
    let mc_runs = 10
  	let run = 0
    set curplot=new          $ create a new plot
	set scratch=$curplot     $ store its name to 'scratch'
    * let cout = unitvec(mc_runs)
    let cutoff=unitvec(mc_runs)
    setseed 11

    dowhile run < mc_runs
        alter C1 = gauss(2e-11, 0.05, 3)
        alter R1 = gauss(1000,0.01,3)
        show C1 : capacitance
        ac dec 40 1e2 100e6

        meas ac ymax MAX v(out)
        let v3db = ymax/sqrt(2)
        meas ac cut when v(out)=v3db fall=last
        let {$scratch}.cutoff[run] = cut

        * set run = $&run
		* set dt = $curplot
		* setplot $scratch

        * let vout{$run} = {$dt}.v(out)
        * let cout[$run] = @c1[capacitance]
        * setplot $dt
		let run = run + 1
    end

    * plot db({$scratch}.allv)
    setplot $scratch
    * print cout cutoff
    wrdata lpf cutoff

.endc

.end


*worst

.control
    define binary(run,index) floor(run/(2^index))-2*floor(run/(2^index+1))
    define wc(nom,tol,index,run,numruns) (run >= numruns) ? nom : (binary(run,index) ? nom*(1+tol) : nom*(1-tol))

    source run.cir
	save out
    let numruns = 4
  	let run = 0
    set curplot=new          $ create a new plot
	set scratch=$curplot     $ store its name to 'scratch'
    * let rout1 = unitvec(numruns+1)
    * let rout2 = unitvec(numruns+1)
    let cutoff=unitvec(numruns+1)

    dowhile run <= numruns
        alter R1 = wc(1000,0.1,0,run,numruns)
        alter R2 = wc(500,0.1,1,run,numruns)

        ac dec 40 1e2 100e6

        meas ac ymax MAX v(N003)
        let v3db = ymax/sqrt(2)
        meas ac cut when v(N003)=v3db fall=last
        let {$scratch}.cutoff[run] = cut

        * set run = $&run
		* set dt = $curplot
		* setplot $scratch

        * let vout{$run} = {$dt}.v(N003)
        * let rout1[$run] = @r1[resistance]
        * let rout2[$run] = @r2[resistance]
        * setplot $dt
		let run = run + 1
    end

    *plot db({$scratch}.allv)
    * plot {$scratch}.cutoff vs {$scratch}.cout
    setplot $scratch
    * print rout1 rout2 cutoff
    wrdata worst $&cutoff

.endc

.end