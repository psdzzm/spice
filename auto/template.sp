*ng_script

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