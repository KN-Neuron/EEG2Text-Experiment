/**
 * @file eeg_manager.h
 * @author Neurotechnology (brainaccess@neurotechnology.com)
 * @brief EEG device manager
 *
 * @copyright Copyright (c) 2022 Neurotechnology
 */

#pragma once

#ifndef __cplusplus
#include <stdbool.h>
#endif //__cplusplus

#include "annotation.h"
#include "battery_info.h"
#include "callbacks.h"
#include "device_info.h"
#include "dllexport.h"
#include "eeg_channel.h"
#include "error.h"
#include "full_battery_info.h"
#include "gain_mode.h"
#include "impedance_measurement_mode.h"
#include "polarity.h"
/**
 * @brief EEG manager typedef. Note that the EEG manager is not thread-safe.
 */
typedef void ba_eeg_manager;

#ifdef __cplusplus
extern "C"
{
#endif //__cplusplus

	/**
	 * @brief Creates a new EEG manager instance
	 *
	 * @details The EEG manager is the primary tool for communicating with the
	 * BrainAccess device
	 *
	 * @return EEG manager instance handle
	 */
	BA_CORE_DLL_EXPORT ba_eeg_manager* ba_eeg_manager_new() NOEXCEPT;

	/**
	 * @brief Destroys an EEG manager instance.
	 *
	 * @details be called exactly once, after the manager is no longer needed
	 *
	 * @param instance Handle of the EEG manager instance to destroy
	 */
	BA_CORE_DLL_EXPORT void ba_eeg_manager_free(ba_eeg_manager* instance) NOEXCEPT;

	/**
	 * @brief Connects to a device and attempts to initialize it.
	 *
	 * @details
	 * You must wait for the callback to complete before doing anything else
	 * with the EEG manager. The boolean parameter of the callback is true if
	 * the connection is successful, false otherwise.
	 *
	 * @param instance Handle of the EEG manager instance to connect to the port
	 * @param index Brainaccess device index
	 * @param callback Function to be called after the connection succeeds
	 * @param data Data to be passed to the callback
	 * @return status if device compatible
	 */

	BA_CORE_DLL_EXPORT ba_error
	ba_eeg_manager_connect(ba_eeg_manager* instance, const char* device_name, ba_callback_future_bool callback, void* data) NOEXCEPT;
	/**
	 * @brief Disconnects the EEG manager from the device, if connected.
	 *
	 * @param instance Handle of the EEG manager to disconnect
	 */
	BA_CORE_DLL_EXPORT void ba_eeg_manager_disconnect(ba_eeg_manager* instance) NOEXCEPT;

	/**
	 * @brief Checks if an EEG manager is connected to any device
	 *
	 * @param instance Handle of the EEG manager to check the connection status
	 * of
	 * @return `true` if EEG manager is connected
	 */
	BA_CORE_DLL_EXPORT bool ba_eeg_manager_is_connected(ba_eeg_manager* instance) NOEXCEPT;

	/**
	 * @brief Starts streaming data from the device
	 *
	 * @details
	 * You must not call this function twice without stopping the stream in
	 * between.
	 *
	 * @param instance Handle of the EEG manager to stream from
	 * @param callback Function to be called after the stream starts
	 * @param data Data to be passed to the callback
	 * @return Error code
	 */
	BA_CORE_DLL_EXPORT ba_error ba_eeg_manager_start_stream(ba_eeg_manager* instance, ba_callback_future_void callback, void* data) NOEXCEPT;

	/**
	 * @brief Stops streaming data from the device
	 *
	 * @details You must not call this function twice without starting the stream in
	 * between. You must not call this function while the stream is not running.
	 *
	 * Calling this function resets all stream settings. If you want to stream
	 * again afterwards, you must re-enable all the channels, biases, gains, and
	 * impedance measurement mode that you set previously.
	 *
	 * @param instance Handle of the EEG manager to stop streaming from
	 * @param callback Function to be called after the stream stops
	 * @param data Data to be passed to the callback
	 * @return Error code
	 */
	BA_CORE_DLL_EXPORT ba_error ba_eeg_manager_stop_stream(ba_eeg_manager* instance, ba_callback_future_void callback, void* data) NOEXCEPT;

	/**
	 * @brief Checks if the device is streaming
	 *
	 * @param instance Handle of the EEG manager to check the streaming status
	 * of
	 * @return `true` if the device is currently streaming
	 */
	BA_CORE_DLL_EXPORT bool ba_eeg_manager_is_streaming(const ba_eeg_manager* instance) NOEXCEPT;

	/**
	 * @brief Loads the configuration from the device
	 *
	 * @details It sends a request to the device
	 * to load its configuration, such as channel settings, biases, gains, and
	 * impedance measurement mode. The callback function is called after the
	 * configuration is loaded.
	 *
	 * @param instance Handle of the EEG Manager instance to load the configuration
	 * of
	 * @param callback Function to be called after the configuration is loaded
	 * @param data Data to be passed to the callback function
	 *
	 * @return Error code indicating the success or failure of the operation
	 */
	BA_CORE_DLL_EXPORT ba_error ba_eeg_manager_load_config(ba_eeg_manager* instance, ba_callback_future_void callback, void* data) NOEXCEPT;

	/**
	 * @brief Gets the standard battery info from an EEG device
	 *
	 * @details The device periodically sends its battery info after an update.
	 * That info is stored in a cache and can be retrieved with this function.
	 *
	 * @param instance Handle of the EEG manager to get the battery info of
	 * @return Cached battery info
	 */
	BA_CORE_DLL_EXPORT const ba_battery_info ba_eeg_manager_get_battery_info(ba_eeg_manager* instance) NOEXCEPT;

	//	/**
	//	 * @brief Gets the extended battery info from an EEG device
	//	 *
	//	 * @details Sends a request to the device for the full battery info. No caching is
	//	 * performed on this data.
	//	 *
	//	 * @param instance Handle of the EEG manager to get the battery info of
	//	 * @param callback Function to be called after the info is received
	//	 * @param data Data to be passed to the callback
	//	 * @return Error code
	//	 */
	//	BA_CORE_DLL_EXPORT ba_error
	//	ba_eeg_manager_get_full_battery_info(ba_eeg_manager* instance, ba_callback_future_full_battery_info callback, void* data) NOEXCEPT;

	/**
	 * @brief Enables the channel on the device and adds the data to the stream
	 * chunks
	 *
	 * @details This function takes effect on stream start, and its effects are
	 * reset by stream stop. Therefore, it must be called with the appropriate
	 * arguments before every stream start.
	 *
	 * @param instance Handle of the EEG Manager instance for which to
	 * enable/disable the channel
	 * @param ch Channel ID of the channel to enable/disable
	 * @param state True for enable, false for disable
	 */
	BA_CORE_DLL_EXPORT void ba_eeg_manager_set_channel_enabled(ba_eeg_manager* instance, ba_eeg_channel ch, bool state) NOEXCEPT;

	/**
	 * @brief Changes gain mode for a channel on the device.
	 *
	 * @details This function takes effect on stream start, and its effects are
	 * reset by stream stop. Therefore, it must be called with the appropriate
	 * arguments before every stream start.
	 *
	 * This only affects channels that support it. For example, it affects the
	 * electrode measurement channels but not sample number or digital input.
	 *
	 * Note that the affected channel data is already multiplied by the gain you
	 * set here.
	 *
	 * @param instance Handle of the EEG Manager instance for which to modify
	 * channel gains
	 * @param ch Channel ID of the channel to modify the gain of
	 * @param g Gain mode
	 */
	BA_CORE_DLL_EXPORT void ba_eeg_manager_set_channel_gain(ba_eeg_manager* instance, ba_eeg_channel ch, ba_gain_mode g) NOEXCEPT;

	/**
	 * @brief Set an electrode channel as a bias electrode
	 *
	 * @details This function takes effect on stream start, and its effects are
	 * reset by stream stop. Therefore, it must be called with the appropriate
	 * arguments before every stream start.
	 *
	 * This only affects channels that support it. For example, it affects the
	 * electrode measurement channels but not sample number or digital input.
	 *
	 * Sets channel that is used for bias feedback. The set channel signal is
	 * used to drive the bias electrode and cable shields to actively cancel
	 * common mode noise such as noise from the mains. Please select channel
	 * that is believed to have a relatively good signal.
	 *
	 * @param instance Handle of the EEG Manager instance for which to set bias
	 * @param ch Channel ID of the electrode to set as bias
	 * @param p Which side of the electrode to use (if device is not
	 * bipolar, use BOTH)
	 */
	BA_CORE_DLL_EXPORT void ba_eeg_manager_set_channel_bias(ba_eeg_manager* instance, ba_eeg_channel ch, ba_polarity p) NOEXCEPT;

	/**
	 * @brief Sets impedance measurement mode
	 *
	 * @details This function takes effect on stream start, and its effects are
	 * reset by stream stop. Therefore, it must be called with the appropriate
	 * arguments before every stream start.
	 *
	 * This function setups device for electrode impedance measurement. It
	 * injects a 7nA certain frequency current through the bias electrodes to
	 * measurement electrodes. Voltage recordings from each channel can then be
	 * used to calculate the impedance for each electrode: Impedance = Vpp/7nA
	 *
	 * @param instance Handle of the EEG Manager instance for which to set
	 * impedance mode
	 * @param mode Impedance mode to set
	 */
	BA_CORE_DLL_EXPORT void ba_eeg_manager_set_impedance_mode(ba_eeg_manager* instance, ba_impedance_measurement_mode mode) NOEXCEPT;

	/**
	 * @brief Get EEG device info
	 *
	 * @details Must not be called unless device connection is successful.
	 *
	 * @param instance Handle of the EEG Manager instance to get the device info
	 * of
	 * @return Info of the currently connected device
	 */
	BA_CORE_DLL_EXPORT const ba_device_info* ba_eeg_manager_get_device_info(const ba_eeg_manager* instance) NOEXCEPT;

	/**
	 * @brief Gets the index of a channel's data into the chunk
	 *
	 * @details Must only be used during stream (after stream start, before
	 * stream stop).
	 *
	 * A chunk is an array of channel data (channel data being an array of
	 * values). To get the index for the channel you're looking for, use this
	 * function.
	 *
	 * If channel was not enabled, returns (size_t)-1
	 *
	 * @param instance Handle of the EEG Manager
	 * @param ch Channel to get the index of
	 * @return Index into chunk representing a channel
	 */
	BA_CORE_DLL_EXPORT size_t ba_eeg_manager_get_channel_index(const ba_eeg_manager* instance, ba_eeg_channel ch) NOEXCEPT;

	/**
	 * @brief Gets device sample rate
	 *
	 * @param instance Handle of the EEG Manager to get the sample frequency of
	 * @return Sample frequency (Hz)
	 */
	BA_CORE_DLL_EXPORT uint16_t ba_eeg_manager_get_sample_frequency(const ba_eeg_manager* instance) NOEXCEPT;

	/**
	 * @brief Sets a callback to be called every time a chunk is available
	 *
	 * @details The callback may or may not run in the reader thread, and as
	 * such, synchronization must be used to avoid race conditions, and the
	 * callback itself must be as short as possible to avoid blocking
	 * communication with the device.
	 *
	 * Set to null to disable.
	 *
	 * @param instance Handle of the EEG Manager to set the callback of
	 * @param callback Function to be called every time a chunk is available
	 * @param data Data to be passed to the callback
	 */
	BA_CORE_DLL_EXPORT void ba_eeg_manager_set_callback_chunk(ba_eeg_manager* instance, ba_callback_chunk callback, void* data) NOEXCEPT;

	/**
	 * @brief Sets a callback to be called every time the battery status is
	 * updated
	 *
	 * @details The callback may or may not run in the reader thread, and as
	 * such, synchronization must be used to avoid race conditions, and the
	 * callback itself must be as short as possible to avoid blocking
	 * communication with the device.
	 *
	 * Set to null to disable.
	 *
	 * @param instance Handle of the EEG Manager to set the callback of
	 * @param callback Function to be called every time a battery update is
	 * available
	 * @param data Data to be passed to the callback
	 */
	BA_CORE_DLL_EXPORT void ba_eeg_manager_set_callback_battery(ba_eeg_manager* instance, ba_callback_battery callback, void* data) NOEXCEPT;

	/**
	 * @brief Sets a callback to be called every time the device disconnects
	 *
	 * @details The callback may or may not run in the reader thread, and as
	 * such, synchronization must be used to avoid race conditions, and the
	 * callback itself must be as short as possible to avoid blocking
	 * communication with the device.
	 *
	 * Set to null to disable.
	 *
	 * @param instance Handle of the EEG Manager to set the callback of
	 * @param callback Function to be called every time the device disconnects
	 * @param data Data to be passed to the callback
	 */
	BA_CORE_DLL_EXPORT void ba_eeg_manager_set_callback_disconnect(ba_eeg_manager* instance, ba_callback_disconnect callback, void* data) NOEXCEPT;

	/**
	 * @brief Add an annotation with the current timestamp and given string
	 *
	 * @details Should not be used before stream start.
	 *
	 * Note that annotations are cleared on disconnect.
	 *
	 * @param instance Handle of the EEG Manager to add an annotation to
	 * @param annotation Annotation string to add
	 */
	BA_CORE_DLL_EXPORT ba_error ba_eeg_manager_annotate(ba_eeg_manager* instance, const char* annotation) NOEXCEPT;

	/**
	 * @brief Start OTA update process
	 *
	 * @details This function must be called after device connection is
	 * successful.
	 *
	 * @param instance Handle of the EEG Manager to add an annotation to
	 * @param callback Function to be called every time the device disconnects
	 * @param data Data to be passed to the callback
	 */
	BA_CORE_DLL_EXPORT ba_error ba_eeg_manager_start_update(ba_eeg_manager* instance, ba_callback_ota_update callback, void* data) NOEXCEPT;

	/**
	 * @brief Retrieve all the annotations accumulated so far
	 *
	 * @details Note that annotations are cleared on disconnect
	 *
	 * @param instance Handle of the EEG Manager to get the annotations from
	 * @param annotations (Output parameter) Annotation array
	 * @param annotations_size (Output parameter) Annotation array size
	 */
	BA_CORE_DLL_EXPORT void ba_eeg_manager_get_annotations(const ba_eeg_manager* instance, ba_annotation** annotations, size_t* annotations_size) NOEXCEPT;

	/**
	 * @brief Clears all accumulated annotations
	 *
	 * @details Note that annotations are cleared on disconnect
	 *
	 * @param instance  Handle of the EEG Manager to clear the annotations for
	 */
	BA_CORE_DLL_EXPORT void ba_eeg_manager_clear_annotations(ba_eeg_manager* instance) NOEXCEPT;

#ifdef __cplusplus
}
#endif //__cplusplus
