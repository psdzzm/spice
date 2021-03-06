* This is supposed to be the model for an MCP6271, but the model
* supplied by MicroChip doesn't work in LTSpice.  I could try to
* hack it, but it's very complicated and I don't want to take the
* time it would require.  Instead I have found the AD8515 SPICE
* Macro-model, from Analog Devices, which is a *little* bit like
* the MCP6271, and I've used that.  LTSpice is OK with this.
*
* The AD8515 has (MCP6271 figures in brackets):
* Single-supply operation: 1.8V to 5V [2 to 5.5V]
* Offset voltage: 6mV maximum [3mV]
* Slew rate: 2.7V/?s [0.9V/us]
* Bandwidth: 5MHz [2MHz]
* Rail-to-rail input and output swing 
* Low input bias current: 2pA typical [1pA]
* Low supply current @ 1.8V: 450 ?A maximum [170uA]
*
* Node Assignments
*			noninverting input
*			|	inverting input
*			|	|	 positive supply
*			|	|	 |	 negative supply
*			|	|	 |	 |	 output
*			|	|	 |	 |	 |
*			|	|	 |	 |	 |
.SUBCKT MCP6271		1	2	99	50	45
* 
* INPUT STAGE
*
M1   4  7  8  8 PIX L=1E-6 W=81.24E-6
M2   6  2  8  8 PIX L=1E-6 W=81.24E-6
M3  11  7 10 10 NIX L=1E-6 W=81.24E-6
M4  12  2 10 10 NIX L=1E-6 W=81.24E-6
RC1  4 14 0.001E+3
RC2  6 16 0.001E+3
RC3 17 11 0.001E+3
RC4 18 12 0.001E+3
RC5 14 50 10E+3
RC6 16 50 10E+3
RC7 99 17 10E+3
RC8 99 18 10E+3
*Set the secondary pole at 17MHz using c1,c2 and RC5..
C1  14 16 0.70E-12
C2  17 18 0.70E-12
I1  99  8 60E-6
I2  10 50 60E-6
V1  99  9 0.3
V2  13 50 0.3
D1   8  9 DX
D2  13 10 DX
EOS  7  1 POLY(3) (22,98) (73,98) (81,98) 1E-3 1 1 1
IOS  1  2 1E-12
*
* CMRR 75dB, ZERO AT 20kHz
*
ECM1 21 98 POLY(2) (1,98) (2,98) 0 .5 .5
RCM1 21 22 281.170E+3
CCM1 21 22 2.83E-11
RCM2 22 98 50
*
* PSRR=85dB, ZERO AT 200Hz
*
RPS1 70  0 1E+6
RPS2 71  0 1E+6
CPS1 99 70 1E-5
CPS2 50 71 1E-5
EPSY 98 72 POLY(2) (70,0) (0,71) 0 1 1
RPS3 72 73 795.774E+3
CPS3 72 73 10.0E-9
RPS4 73 98 44.74
*
* VOLTAGE NOISE REFERENCE OF 20nV/rt(Hz)
*
VN1 80 98 0
RN1 80 98 16.45E-3
HN  81 98 VN1 22
RN2 81 98 1
*
* INTERNAL VOLTAGE REFERENCE
*
EREF 98  0 POLY(2) (99,0) (50,0) 0 .5 .5
GSY  99 50 (99,50) 4E-6 
EVP  97 98 (99,50) 0.5
EVN  51 98 (50,99) 0.5
*
* LHP ZERO AT 17MHz, POLE AT 83.9MHz
*
E1 32 98 POLY(2) (4,6) (11,12) 0 .6270 .6270
R2 32 33 2.378E+3
R3 33 98 9.362E+3
C3 32 33 1E-12
*
* GAIN STAGE
*
G1 98 30 (33,98) 6.3E-5
R1 30 98 1.48E+8
CF 45 30 13.2E-12
D3 30 97 DX
D4 51 30 DX
*
* OUTPUT STAGE
*
M5  45 46 99 99 POX L=1E-6 W=3.23E-3
M6  45 47 50 50 NOX L=1E-6 W=3.58E-3
EG1 99 46 POLY(1) (98,30) 0.4394 1
EG2 47 50 POLY(1) (30,98) 0.4336 1
*
* MODELS
*
.MODEL POX PMOS (LEVEL=2,KP=10E-6,VTO=-0.328,LAMBDA=0.01,RD=0)
.MODEL NOX NMOS (LEVEL=2,KP=10E-6,VTO=+0.328,LAMBDA=0.01,RD=0)
.MODEL PIX PMOS (LEVEL=2,KP=100E-6,VTO=-1,LAMBDA=0.01)
.MODEL NIX NMOS (LEVEL=2,KP=100E-6,VTO=+1,LAMBDA=0.01)
.MODEL DX D(IS=1E-14,RS=5)
.ENDS MCP6271










