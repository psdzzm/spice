*ng_script

.control
	define binary(run,index) floor(run/(2^index))-2*floor(run/(2^index+1))
	define wc(nom,tol,index,run,numruns) (run >= numruns) ? nom : (binary(run,index) ? nom*(1+tol) : nom*(1-tol))

	source run.cir
	save out
	let numruns = 8
	let run = 0
	set curplot=new          $ create a new plot
	set scratch=$curplot     $ store its name to 'scratch'
	let cutoff=unitvec(numruns+1)
	dowhile run <= numruns
		alter c1=wc(2e-12,0.95,0,run,numruns)
		alter c2=wc(7e-13,0.05,1,run,numruns)
		alter r1=wc(39000,0.01,2,run,numruns)
		ac dec 40 2371374.0 387687500.0

		meas ac ymax MAX v(out)
		let v3db = ymax/sqrt(2)
		meas ac cut when v(out)=v3db fall=last
		let {$scratch}.cutoff[run] = cut
		let run = run + 1
	end

	setplot $scratch
	wrdata fc_wst cutoff
.endc

.end