/*
 * dlog.h
 *
 *  Created on: Oct 10, 2024
 *      Author: bofh
 */

#ifndef DLOG_H_
#define DLOG_H_

#include <stddef.h>
#include "post.h"
#ifdef POST_DUMP
#  define DLOG
#endif

#define P32(X) dlog(#X ": %08lx\r\n",X)

#ifdef DLOG
void dlog(const char *fmt, ...);
void dlog_process_action(void);
void dlog_dump(void);
#else
#define dlog(X,...)
#endif

#endif /* DLOG_H_ */
