#include "dlog.h"

#ifdef DLOG
#include <stdarg.h>
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include "em_usart.h"
#include "em_cmu.h"

static char dlogBuffer[4192];
static size_t dlogFill = 0;
static int dlogError = 0;
static bool ready = false;

void vcom_send(const char*data) {
  static bool initialized = false;
  if(!initialized) {
      CMU_ClockEnable(cmuClock_USART1, true);
      USART_InitAsync_TypeDef init = USART_INITASYNC_DEFAULT;
      GPIO->USARTROUTE[1].TXROUTE = (gpioPortA << _GPIO_USART_TXROUTE_PORT_SHIFT) | (5 << _GPIO_USART_TXROUTE_PIN_SHIFT);
      GPIO->USARTROUTE[1].RXROUTE = (gpioPortA << _GPIO_USART_RXROUTE_PORT_SHIFT) | (5 << _GPIO_USART_RXROUTE_PIN_SHIFT);
      GPIO->USARTROUTE[1].ROUTEEN = _GPIO_USART_ROUTEEN_TXPEN_MASK | _GPIO_USART_ROUTEEN_RXPEN_MASK;
      USART_InitAsync(USART1, &init);
      GPIO_PinModeSet(gpioPortA, 5, gpioModePushPull, 1);
      GPIO_PinModeSet(gpioPortA, 6, gpioModeInput, 1);
      initialized = true;
  }
  while(*data) {
      USART_Tx(USART1,*data);
      data++;
  }
}

void dlog(const char *fmt, ...) {
  va_list args;
  if(dlogFill >= sizeof(dlogBuffer)) return;
  va_start(args, fmt);
  int length = vsprintf(&dlogBuffer[dlogFill], fmt, args);
  va_end(args);
  if(length < 0) {
      dlogError = length;
      return;
  }
  dlogFill += length;
}

void dlog_process_action(void) {
  if(!ready) return;
  if(dlogError) {
      char buf[12];
      vcom_send("dlogError: ");
      sprintf(buf,"%d",dlogError);
      vcom_send(buf);
      vcom_send("\r\n");
      dlogError = 0;
  }
  if(dlogFill >= sizeof(dlogBuffer)) {
      vcom_send("dlogBuffer overrun\r\n");
  }
  if(dlogFill > 0) {
      vcom_send(dlogBuffer);
      dlogFill = 0;
      memset(dlogBuffer,0,sizeof(dlogBuffer));
  }
}

void dlog_dump(void) {
  ready = true;
}

#endif
