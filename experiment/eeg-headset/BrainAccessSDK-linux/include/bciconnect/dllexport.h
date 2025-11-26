#pragma once

// Define BA_BCICONNECT_DLL_EXPORT for any platform
#if defined _WIN32 || defined __CYGWIN__
	#ifdef BA_BCICONNECT_DLL_IS_EXPORTING
		// Exporting...
		#ifdef __GNUC__
			#define BA_BCICONNECT_DLL_EXPORT __attribute__ ((dllexport))
		#else
			// Note: actually gcc seems to also supports this syntax.
			#define BA_BCICONNECT_DLL_EXPORT __declspec(dllexport)
		#endif
	#else
		#ifdef __GNUC__
			#define BA_BCICONNECT_DLL_EXPORT __attribute__ ((dllimport))
		#else
			// Note: actually gcc seems to also supports this syntax.
			#define BA_BCICONNECT_DLL_EXPORT __declspec(dllimport)
		#endif
	#endif
	#define NOT_BA_BCICONNECT_DLL_EXPORT
#else
	#if __GNUC__ >= 4
		#define BA_BCICONNECT_DLL_EXPORT __attribute__ ((visibility ("default")))
		#define NOT_BA_BCICONNECT_DLL_EXPORT  __attribute__ ((visibility ("hidden")))
	#else
		#define BA_BCICONNECT_DLL_EXPORT
		#define NOT_BA_BCICONNECT_DLL_EXPORT
	#endif
#endif
