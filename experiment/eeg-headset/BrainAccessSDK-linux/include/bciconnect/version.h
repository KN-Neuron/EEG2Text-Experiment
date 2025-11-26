/**
 * @file version.h
 * @author Neurotechnology (brainaccess@neurotechnology.com)
 * @brief Version numbers
 *
 * @copyright Copyright (c) 2022 Neurotechnology
 */

#pragma once

#include <stdint.h>
#include "noexcept.h"
#include "dllexport.h"

 /**
  * @brief Struct describing version numbers
  *
  * @details Uses semantic versioning
  */
typedef struct
{
	uint8_t major; ///< API-breaking changes
	uint8_t minor; ///< Feature updates
	uint8_t patch; ///< Bugfixes
} ba_version;

#ifdef __cplusplus
extern "C"
{
#endif //__cplusplus

/**
* @brief Returns the installed library's actual version
* @details Uses semantic versioning
*
* @return Installed library's actual version
*/
BA_BCICONNECT_DLL_EXPORT const ba_version* ba_bci_connect_get_version() NOEXCEPT;

#ifdef __cplusplus
}
#endif //__cplusplus
