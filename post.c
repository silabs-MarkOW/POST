#include "em_gpio.h"
#include "post.h"
#include "dlog.h"
#include "em_cmu.h"
#include <stddef.h>

#ifdef POST_ACTIVE
#ifdef POST_DUMP
static struct {
  const char *file;
  int line;
} lines[64];
#endif
static size_t index;

void post_init(void) {
  CMU_ClockEnable(cmuClock_GPIO, true);
  index = 0;
  for(int i = 0; i < 5; i++) {
      GPIO_PinModeSet(gpioPortB, i, gpioModePushPull, 0);
  }
  for(int i = 0; i < 2; i++) {
      GPIO_PinModeSet(gpioPortC, i, gpioModePushPull, 0);
  }
}

#ifdef POST_DUMP
void post(const char *file, int line) {
  lines[index].file = file;
  lines[index].line = line;
#else
void post(void) {
#endif
  GPIO->P[1].DOUT = index & 0x1f;
  GPIO->P[2].DOUT = (index & 0x1e0) >> 5;
  index++;
}

#ifdef POST_DUMP
void post_dump(void) {
  for(size_t i = 0; i < index; i++) {
      dlog("%d:%d:%s\r\n",i,lines[i].line,lines[i].file);
  }
  dlog("\x04");
  dlog_dump();
}
#endif
#endif
