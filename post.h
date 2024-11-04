#ifndef POST_H_
#define POST_H_

#define POST_ACTIVE
#ifdef POST_ACTIVE
//#define POST_DUMP
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
