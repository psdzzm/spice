You should be able to download LT Spice for MS Windows (or Mac OS) from here:

https://www.analog.com/en/design-center/design-tools-and-calculators/ltspice-simulator.html

Install the latest version LTSpice (V17 at time of writing) into the default location.

In Windows, navigate to C:\Users\XXX\Documents\LTspiceXVII

Where "XXX" denotes your username in Windows

There you will find a directory "sub".  Copy the contents of the directory "sub_additions" (where this README.txt file is located) into directory "sub".  Copy the contents of the directory "sym_additions" into directory "sym".

Doing this adds models for the MCP6271 opamp into the LT Spice library.  

If you then instantiate the device by clicking the "Component" icon in the top menu bar (looks like an AND gate), and selecting MCP6271, you will get the component into your schematic.

If you upgrade LTSpice, or re-install it, the files provided may will be lost.  Keep these copies!

Notes on Model:

* The MicroChip model for the MCP6271 is enormously complex, so we use a simplified version instead.

JST 20/11/20



