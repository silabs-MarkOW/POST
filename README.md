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
* <code>POST_DUMP</code>  If this is not defined, only the code to control GPIO is linked.  If defined, the file and line nnumber of each <code>POST()</code> macro is recored, allowing this to be dumped via dlog.  It is not strictly necessary for dlog to be used, but it was already implemented.

## dlog
dlog provides a printf type logging.  Output is recorded to a
buffer.  Buffer can be sent to UART via <code>dlog_action_process()</code> after <code>dlog_dump()</code> is called.  I.e. this allows logging before UART is enabled.

