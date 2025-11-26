/**
 * @file bacore.h
 * @author Neurotechnology (brainaccess@neurotechnology.com)
 * @brief Core library info and lifecycle API
 *
 * @copyright Copyright (c) 2022 Neurotechnology
 */

#pragma once

#include "dllexport.h"
#include "log_level.h"
#include "version.h"
#include <stdio.h>

#define BA_CONFIG_DEFAULT_PATH "bacore.json"

#define BA_CONFIG_DEFAULT_LOG_BUFFER_SIZE     512
#define BA_CONFIG_DEFAULT_LOG_PATH            "bacore.log"
#define BA_CONFIG_DEFAULT_LOG_LEVEL           2
#define BA_CONFIG_DEFAULT_APPEND_LOGS         false
#define BA_CONFIG_DEFAULT_TIMESTAMPS_ENABLED  true
#define BA_CONFIG_DEFAULT_AUTOFLUSH           true
#define BA_CONFIG_DEFAULT_THREADS_IDS_ENABLED true
#define BA_CONFIG_DEFAULT_CHUNK_SIZE          25
#define BA_CONFIG_DEFAULT_ENABLE_LOGS         true
#define BA_CONFIG_DEFAULT_UPDATE_FILE         "../updates/firmware_HALO.bin"

/**
 * @brief Unknown error while calling `ba_core_init()`
 */
#define BA_INIT_ERROR_UNKNOWN 0xFF

/**
 * @brief Initialized successfully
 */
#define BA_INIT_ERROR_OK 0

/**
 * @brief Configuration file contains a value of the wrong type
 */
#define BA_INIT_ERROR_CONFIG_TYPE 1

/**
 * @brief Bluetooth adapter value is wrong
 */
#define BA_INIT_ERROR_WRONG_ADAPTER_VALUE 2

/**
 * @brief The version requested and the version
 */
#define BA_INIT_ERROR_INCOMPATIBLE_VERSION 3

/**
 * @brief The Bluetooth is not enabled
 */
#define BA_INIT_ERROR_NOT_ENABLED 4

/**
 * @brief The Bluetooth adapter is not found
 */
#define BA_INIT_ERROR_NOT_FOUND 5

/**
 * @brief Configuration file could not be parsed, invalid JSON or missing value
 */
#define BA_INIT_ERROR_CONFIG_PARSE 6

/**
 * @brief Error codes for init
 */
typedef uint8_t ba_init_error;

// typedef struct
//{
//	int size;
//	SimpleBLE::Peripheral* devices;
// } BLEDevices;

#ifdef __cplusplus
extern "C"
{
#endif //__cplusplus

	/**
	 * @brief Initializes the library. Must be called before any other BrainAccess
	 * Core library function. Only call once.
	 *
	 * @details This function reads the config file, starts logging, etc. It first
	 * checks if the version of the library that the application expects and the
	 * version of the library installed are compatible.
	 *
	 * @param version The version of the library that the application expects.
	 * @return Error code
	 */
	BA_CORE_DLL_EXPORT ba_init_error ba_core_init() NOEXCEPT;

	/**
	 * @brief Returns the installed library's actual version
	 * @details Uses semantic versioning
	 *
	 * @return Installed library's actual version
	 */
	BA_CORE_DLL_EXPORT const ba_version* ba_core_get_version() NOEXCEPT;

	/**
	 * @brief Returns the number of BrainAccess devices currently connected
	 *
	 * @details This function scans for BrainAccess devices and returns the count of
	 * devices currently connected.
	 *
	 * @return Number of connected BrainAccess devices
	 */
	BA_CORE_DLL_EXPORT int ba_core_device_count() NOEXCEPT;

	/**
	 * @brief Retrieves the name of a BrainAccess device at a specific index
	 *
	 * @details This function retrieves the name of a BrainAccess device at the given
	 * index. The name is stored in the provided character array.
	 *
	 * @param name Character array to store the device name
	 * @param index Index of the device whose name needs to be retrieved
	 */
	BA_CORE_DLL_EXPORT void ba_core_device_get_name(char* name, int index) NOEXCEPT;

	/**
	 * @brief Retrieves the address of a BrainAccess device at a specific index
	 *
	 * @details This function retrieves the address of a BrainAccess device at the given
	 * index. The address is stored in the provided character array.
	 *
	 * @param address Character array to store the device address
	 * @param index Index of the device whose address needs to be retrieved
	 */
	BA_CORE_DLL_EXPORT void ba_core_device_get_address(char* address, int index) NOEXCEPT;

	/**
	 * @brief Sets config of logs level
	 * @details Must be called after ba_core_init() and before ba_core_close().
	 * @param level log level.
	 * @default Warning.
	 * @return Error code
	 */
	BA_CORE_DLL_EXPORT ba_init_error ba_core_config_set_log_level(ba_log_level level) NOEXCEPT;

	/**
	 * @brief Sets config of chunk size
	 * @details Must be called after ba_core_init() and before ba_core_close().
	 * @param chunk_size chunk size.
	 * @default 25
	 * @return Error code
	 */
	BA_CORE_DLL_EXPORT ba_init_error ba_core_config_set_chunk_size(int chunk_size) NOEXCEPT;

	/**
	 * @brief Sets config to enable logging
	 * @details Must be called after ba_core_init() and before ba_core_close().
	 *
	 * @param enabled true if logging enable, otherwise - false
	 * @return Error code
	 */
	BA_CORE_DLL_EXPORT ba_init_error ba_core_config_enable_logging(bool enable) NOEXCEPT;

	/**
	 * @brief Sets config buffer parameters
	 * @details Use this if you want to change logs path, enable/disable append or change logs buffer size.
	 * Must be called after ba_core_init() and before ba_core_close().
	 *
	 * @param path where to store log file and it's name with .log.
	 * @param append enable/disable append to log file.
	 * @param buffer_size log buffer size.
	 * @return Error code.
	 */
	BA_CORE_DLL_EXPORT ba_init_error ba_core_set_core_log_path(const char* path, bool append, int buffer_size) NOEXCEPT;

	/**
	 * @brief Sets config of update file path
	 * @details Must be called after ba_core_init() and before ba_core_close().
	 *
	 * @param path path to the update file.
	 */
	BA_CORE_DLL_EXPORT ba_init_error ba_core_config_set_update_path(const char* path) NOEXCEPT;

	/**
	 * @brief Enable timestamps in logs
	 * @details Must be called after ba_core_init() and before ba_core_close().
	 *
	 * @param enable true if show timestamps, false - hide.
	 * @return Error code
	 */
	BA_CORE_DLL_EXPORT ba_init_error ba_core_config_timestamp(bool enable) NOEXCEPT;

	/**
	 * @brief Enable autoflush
	 * @details Must be called after ba_core_init() and before ba_core_close().
	 *
	 * @param enable true if enable autoflush, false - disable.
	 * @return Error code
	 */
	BA_CORE_DLL_EXPORT ba_init_error ba_core_config_autoflush(bool enable) NOEXCEPT;

	/**
	 * @brief Enable Thread ID.
	 * @details Enable thread id print in logs. Must be called after ba_core_init() and before ba_core_close().
	 *
	 * @param enable
	 * @return Error code
	 */
	BA_CORE_DLL_EXPORT ba_init_error ba_core_config_thread_id(bool enable) NOEXCEPT;

	/**
	 * @brief Scan for Brainaccess devices.
	 * @details This function scans for BrainAccess devices and adds them to parameter
	 * devices array. Devices pointer bust be dealocated.
	 *
	 * @param devices device array pointer.
	 * @param adapter_index index of adapter to be used (default value 0).
	 * @return Error code
	 */
	BA_CORE_DLL_EXPORT ba_init_error ba_core_scan(const char** device_list, size_t* device_list_size) NOEXCEPT;

	/**
	 * @brief Closes the library and cleans up afterwards. Must be called after all
	 * BrainAccess Core libary functions used by the application. Only call once.
	 *
	 * @details If `ba_core_init()` failed, do not call this function.
	 */
	BA_CORE_DLL_EXPORT void ba_core_close() NOEXCEPT;

#ifdef __cplusplus
}
#endif //__cplusplus
