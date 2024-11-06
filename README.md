# C Sources
These can just be copied into an existing project.  After initialization via<code>post_init()</code> the macro <code>POST()</code> may be used.  Each call to <pde>POST()</code> increments the internally stored state exposed on GPIO lines.  This was developed for BRD2710A (EFR32MG22E) which helpfully exposes several GPIO ports with relatively long sequential pins: PB00...PB04 and P00...PC03.  This allows setting multiple pins in a single port write.
<pre>
  GPIO->P[1].DOUT = index & 0x1f;
  GPIO->P[2].DOUT = (index & 0x1e0) >> 5;
</pre>
<pre>
                  +-------------+
             PC07 |o           o| RST
             PA04 |o           o| PA00
              GND |o           o| GND
               5V |o           o| VMCU
             PD03 |o           o| PC00 ---- bit 5
             PD02 |o           o| PC01 ---- bit 6
  bit 1 ---- PB01 |o           o| PC02 ---- bit 7
  bit 2 ---- PB02 |o           o| PC03 ---- bit 8
  bit 3 ---- PB03 |o           o| PC06
  bit 4 ---- PB04 |o           o| PB00 ---- bit 0
                  +----[USB]----+
</pre>

Operation is controlled by defintions in <code>post.h</code>.
* <code>POST_ACTIVE</code> If this is not defined, calls to <code>post_init()</code> and <code>POST()</code> are defined to no code to allow measurement any instrumentation.
* <code>POST_DUMP</code>  If this is not defined, only the code to control GPIO is linked.  If defined, the file and line nnumber of each <code>POST()</code> macro is recored, allowing this to be dumped via dlog.  It is not strictly necessary for dlog to be used, but it was already implemented.  Output generated as
<pre>
0:__LINE__:__FILE__
1:__LINE__:__FILE__
...
n:__LINE__:__FILE__
EOF
</pre>
Where <code>EOF</code> is ASCII character 0x04.
## dlog
dlog provides a printf type logging.  Output is recorded to a
buffer.  Buffer can be sent to UART via <code>dlog_action_process()</code> after <code>dlog_dump()</code> is called.  I.e. this allows logging before UART is enabled.

# Python code
## capture.py
Simply reads from specifed UART dumping data into file until hitting EOF.
usage: capture.py [-h] [--uart UART] [--output OUTPUT] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  --uart UART           WSTK VCOM UART
  --output OUTPUT, -o OUTPUT
                        File to save post_dump() output
  --debug               echo data to stdout

## aem.py
Script to capture AEM data from WST.
<pre>
usage: aem.py [-h] [--project PROJECT] [--wstk WSTK] [--csv CSV]
              [--duration DURATION] [--trigger TRIGGER]

optional arguments:
  -h, --help           show this help message and exit
  --project PROJECT    Project root folder
  --wstk WSTK          Serial number of WSTK to perform AEM
  --csv CSV            Datafile
  --duration DURATION  Duration of AEM sampling (s)
  --trigger TRIGGER    Trigger level (mA)
</pre>
Current workflow:
* hold reset on WSTK, run with trigger set to 0 (default) to measure range.
* run with trigger set slightly above highest value observed above
<pre>
$ python3 aem.py --duration .1 --wstk 440305827
Running "commander aem dump -s 440305827 -o aem.csv --duration 0.1"
Logging...
Closed file 'aem.csv',
10002 lines written to file.
DONE
Mean: 0.238 mA
Range: -0.0 - 0.8 mA
</pre>

<pre>
$ python3 aem.py --duration .1 --wstk 440305827 --trigger 0.95
Running "commander aem dump -s 440305827 -o aem.csv --duration 0.1 --triggerabove 0.950"
Logging...
Waiting for trigger (current above 0.95 mA)...
Triggered at timestamp: 240465175005 [us], 1.24506 seconds after sampling started.
Closed file 'aem.csv',
10002 lines written to file.
DONE
</pre>

## show-post.py
Cross references output of <code>capture.py</code>, Saleae captured data and optionally AEM data from <code>aem.py</code>.
<pre>
usage: show-post.py [-h] [--project PROJECT] [--xref XREF] [--saleae SALEAE]
                    [--above ABOVE] [--current CURRENT] [--duration DURATION]
                    [--offset OFFSET] [--em4wake]

optional arguments:
  -h, --help           show this help message and exit
  --project PROJECT    Project root folder
  --xref XREF          File containing UART output
  --saleae SALEAE      CSV from saleae
  --above ABOVE        Lower limit (s)
  --current CURRENT    AEM current data file
  --duration DURATION  Plot duration (ms)
  --offset OFFSET      Plot offset (ms)
  --em4wake            Saleae Ch8 is connected to EM4wake button, t=0 at
                       falling edge, default is t=0 at rising edge of RESET
</pre>
