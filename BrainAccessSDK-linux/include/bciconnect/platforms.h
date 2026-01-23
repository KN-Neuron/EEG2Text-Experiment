#pragma once

#if defined(_WIN32) || defined(_WIN64)
	#define __PLATFORM_WINDOWS__
#elif defined(__linux__)
	#define __PLATFORM_LINUX__
#endif
