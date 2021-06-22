*ng_script

.control
	define binary(run,index) floor(run/(2^index))-2*floor(run/(2^index+1))
	define wc(nom,tol,index,run,numruns) (run >= numruns) ? nom : (binary(run,index) ? nom*(1+tol) : nom*(1-tol))

	source run.cir
	save out
	let numruns = 256
	let run = 0
	set curplot=new          $ create a new plot
	set scratch=$curplot     $ store its name to 'scratch'
	let cutoff=unitvec(numruns+1)
	dowhile run <= numruns
		alter c1=wc(2e-09,0.05,0,run,numruns)
		alter c10=wc(1e-09,0.05,1,run,numruns)
		alter c2=wc(1e-09,0.05,2,run,numruns)
		alter r1=wc(11200,0.01,3,run,numruns)
		alter r10=wc(15900,0.01,4,run,numruns)
		alter r2=wc(11200,0.01,5,run,numruns)
		alter ra=wc(1e+08,0.01,6,run,numruns)
		alter rb=wc(1,0.01,7,run,numruns)
		ac dec 40 0.1 50118.810000000005

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