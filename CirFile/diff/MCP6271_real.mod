.SUBCKT MCP6271 1 2 3 4 5
*               | | | | |
*               | | | | Output
*               | | | Negative Supply
*               | | Positive Supply
*               | Inverting Input
*               Non-inverting Input
*
*
* The following op-amps are covered by this model (which came from MicroChip):
*      MCP6271, MCP6271R, MCP6272, MCP6273, MCP6274, MCP6275
*
* Supported:
*      Typical performance for temperature range (-40 to 125) degrees Celsius
*      DC, AC, Transient, and Noise analyses.
*      Most specs, including: offsets, DC PSRR, DC CMRR, input impedance,
*            open loop gain, voltage ranges, supply current, ... , etc.
*      Temperature effects for Ibias, Iquiescent, Iout short circuit 
*            current, Vsat on both rails, Slew Rate vs. Temp and P.S.
*
* Not Supported:
*      Chip select (MCP6273,MCP6275)
*      Some Variation in specs vs. Power Supply Voltage
*      Monte Carlo (Vos, Ib), Process variation
*      Distortion (detailed non-linear behavior)
*      Behavior outside normal operating region
*
* Input Stage
V10  3 10 -500M
R10 10 11 690K
R11 10 12 690K
G10 10 11 10 11 144U
G11 10 12 10 12 144U
C11 11 12 1.0P
C12  1  0 6.00P
E12 71 14 POLY(4) 20 0 21 0 26 0 27 0   2.00M 15 15 1 1
G12 1 0 62 0 1m
M12 11 14 15 15 NMI
G13 1 2 62 0 .22m 
M14 12 2 15 15 NMI 
G14 2 0 62 0 1m
C14  2  0 6.00P
I15 15 4 50.0U
V16 16 4 -300M
GD16 16 1 TABLE {V(16,1)} ((-100,-1p)(0,0)(1m,1u)(2m,1m)) 
V13 3 13 -300M
GD13 2 13 TABLE {V(2,13)} ((-100,-1p)(0,0)(1m,1u)(2m,1m)) 
R71  1  0 20E12
R72  2  0 20E12
R73  1  2 20E12
I80  1  2 300E-15
*
* Noise, PSRR, and CMRR
I20 21 20 423U
D20 20  0 DN1
D21  0 21 DN1
G26  0 26 POLY(2) 3 0 4 0   0.00 -63U -26U
R26 26  0 1
E271 275 0 1 0 1
E272 276 0 2 0 1
R271 275 271 18.51k
R272 276 272 18.51k
R273 271 0 1k
R274 272 0 1k
C271 275 271 0.9p
C272 276 272 0.9p
G27  0 27 POLY(2) 271 0 272 0  -97.8U 100U 100U	
R27 27  0 1
*
* Open Loop Gain, Slew Rate
G30  0 30 12 11 1
R30 30  0 1.00K
G31 0 31 3 4 5.00
I31 0 31 DC 48.6
R31 31  0 1 TC=3.37M,856N
GD31 30 0 TABLE {V(30,31)} ((-100,-1n)(0,0)(1m,0.1)(2m,2))
G32 32 0 3 4 2.00
I32 32 0 DC 81.7
R32 32  0 1 TC=2.47M,-4.55U
GD32 0 30 TABLE {V(30,32)} ((-2m,2)(-1m,0.1)(0,0)(100,-1n))
G33  0 33 30 0 1m
R33  33 0 1K
G34  0 34 33 0 316M
R34  34 0 1K
C34  34 0 21U
G37  0 37 34 0 1m
R37  37 0 1K
C37  37 0 10P
G38  0 38 37 0 1m
R38  39 0 1K
L38  38 39 28U
E38  35 0 38 0 1
G35 33 0 TABLE {V(35,3)} ((-1,-1n)(0,0)(25.0,1n))(26.0,1))
G36 33 0 TABLE {V(35,4)} ((-26.0,-1)((-25.0,-1n)(0,0)(1,1n))
*
* Output Stage
R80 50 0 100MEG
G50 0 50 57 96 2
R58 57  96 0.50
R57 57  0 500
C58  5  0 2.00P
G57  0 57 POLY(3) 3 0 4 0 35 0   0 7.5M 9M 2.00M
GD55 55 57 TABLE {V(55,57)} ((-2m,-1)(-1m,-1m)(0,0)(10,1n))
GD56 57 56 TABLE {V(57,56)} ((-2m,-1)(-1m,-1m)(0,0)(10,1n))
E55 55  0 POLY(2) 3 0 51 0 -1.07M 1 -19.5M
E56 56  0 POLY(2) 4 0 52 0 1.5M 1 -28.3M 0 0 -1.1M
R51 51 0 1k
R52 52 0 1k
GD51 50 51 TABLE {V(50,51)} ((-10,-1n)(0,0)(1m,1m)(2m,1))
GD52 50 52 TABLE {V(50,52)}  ((-2m,-1)(-1m,-1m)(0,0)(10,1n))
G53  3  0 POLY(1) 51 0  -50.0U 1M
G54  0  4 POLY(1) 52 0  -50.0U -1M
*
* Current Limit
G99 96 5 99 0 1
R98 0 98 1 TC=1.91M,-7.05U		
G97 0 98 TABLE { V(96,5) } ((-11.0,-25.0M)(-1.00M,-24.7M)(0,0)(1.00M,24.7M)(11.0,25.0M))		
E97 99 0 VALUE { V(98)*((V(3)-V(4))*26.6M + 933M)}		
D98 4 5 DESD
D99 5 3 DESD
*
* Temperature / Voltage Sensitive IQuiscent
R61 0 61 1 TC=1.6M,3.6U
G61 3 4 61 0 1
G60 0 61 TABLE {V(3, 4)} 
+ ((0,0)(0.7,.2U)(0.8,4U)(1.18,108U)(1.24,70U)
+ (1.38,75U)(1.6,140U)(1.7,150U)(5.5,165U))
*
* Temperature Sensistive offset voltage
I73 0 70 DC 1uA
R74 0 70 1 TC=1.7
E75 1 71 70 0 1 
*
* Temp Sensistive IBias
I62 0 62 DC 1uA
R62 0 62 REXP  190U
*
* Models
.MODEL NMI NMOS(L=2.00U W=42.0U KP=20.0U LEVEL=1 )
.MODEL DESD  D   N=1 IS=1.00E-15
.MODEL DN1 D   IS=1P KF=0.145F AF=1
.MODEL REXP RES TCE= 9
.ENDS MCP6271
