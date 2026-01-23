/**
 * @file error.h
 * @author Neurotechnology (brainaccess@neurotechnology.com)
 * @brief This file defines error codes used in the library.
 *
 * @copyright Copyright (c) 2022 Neurotechnology
 */

#pragma once

#include <stdint.h>

/**
 * @brief No error.
 */
#define BA_ERROR_OK 0

/**
 * @brief Connection error.
 */
#define BA_ERROR_CONNECTION 1

/**
 * @brief Unsupported device error.
 */
#define BA_ERROR_UNSUPPORTED_DEVICE 2

/**
 * @brief Wrong value error.
 */
#define BA_ERROR_WRONG_VALUE 3

/**
 * @brief Bluetooth disabled error.
 */
#define BA_ERROR_BLUETOOTH_DISABLED 4

/**
 * @brief Bluetooth adapter not found error.
 */
#define BA_ERROR_BLUETOOTH_ADAPTER_NOT_FOUND 5

/**
 * @brief Adapter out of index error.
 */
#define BA_ERROR_ADAPTER_OUT_OF_INDEX 6

/**
 * @brief OTA update file not found.
 */
#define BA_ERROR_UPDATE_FILE_NOT_FOUND 7

/**
 * @brief OTA update initiated unsuccessfully.
 */
#define BA_ERROR_UPDATE_INITIATED_UNSUCCESSFULLY 8

/**
 * @brief OTA update failed, device disconnect.
 */
#define BA_ERROR_UPDATE_FAILED_DEVICE_DISCONNECTED 9

/**
 * @brief Unavailable to set annotation. Calibrating, try in few seconds
 */
#define BA_ERROR_ANNOTATION_UNAVAILABLE_CALIBRATING 10

/**
 * @brief 0 devices was found
 */
#define BA_ERROR_NO_DEVICES_FOUND 11

/**
 * @brief Unknown error.
 */
#define BA_ERROR_UNKNOWN 0xFF

/**
 * @brief Type definition for error code.
 */
typedef uint8_t ba_error;