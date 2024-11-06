#ifndef POST_H_
#define POST_H_

/*
 * Modify behavior via POST_ACTIVE and POST_DUMP
 * if POST_ACTIVE not defined, post_init() and POST() generate no code
 * if POST_DUMP is defined, locations of POST() calls are saved and may be
 * dumped to UART using post_dump()
 */
#define POST_ACTIVE
#ifdef POST_ACTIVE

#define POST_DUMP

#include "dlog.h"
#ifdef POST_DUMP
#define POST() post(__FILE__,__LINE__)
void post(const char *file, int line);
void post_dump(void);
#else
#define POST() post()
void post(void);
#endif

void post_init(void);
#else
#define POST()
#define post_init()
#endif

#endif /* POST_H_ */
