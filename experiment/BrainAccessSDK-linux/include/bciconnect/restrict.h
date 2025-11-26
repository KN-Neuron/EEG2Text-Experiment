#pragma once

#include "platforms.h"

#ifdef __cplusplus
	#ifdef __PLATFORM_LINUX__
		#define restrict __restrict
	#else
		#define restrict
	#endif
#endif
