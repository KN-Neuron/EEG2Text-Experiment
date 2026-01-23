/**
 * @file processor.h
 * @author UAB Neurotechnology (brainaccess@neurotechnology.com)
 * @brief EEG signal processing
 *
 * @copyright Copyright (c) 2023 Neurotechnology
 */

#pragma once

#include "dllexport.h"
#include "noexcept.h"
#include <stddef.h>

#ifdef __cplusplus
extern "C"
{
#endif

/**
* @brief Estimates the EEG signal quality
*
* @details This function estimates the EEG signal quality for each channel based
* on amplitude variation and 50/60Hz noise level. The supplied data should be
* unprocessed of 2-3 seconds length. If signals do not pass the quality measures
* of this function, then it means that they are really corrupted or the electrodes
* are not fitted. Eye or muscle artifacts are not evaluated by this function, signals
* containing theses should still pass the quality measures.
* 
* @param x a pointer to an array containing EEG signals from different channels,
* channel n data should start at position x[n_chans * n_time_steps],
* total length of x array should be n_chans * n_time_steps
* @param n_chans number of recording channels
* @param n_time_steps number of time samples in each channel recording
* @param quality a pointer to an array which returns the quality of each channel,
* its length should be n_chans. Possible quality values:
* 0 - signal is bad and did not pass any quality measure
* 1 - signal passed amplitude related quality measures
* 2 - signal also do not contain significant amounts of 50/60Hz noise
*/
BA_BCICONNECT_DLL_EXPORT void ba_bci_connect_get_signal_quality(double* x, const size_t n_chans, const size_t n_time_steps, double fs, double* quality) NOEXCEPT;

/**
* @brief Detrends EEG signals
*
* @details This function subtracts the linear fit from EEG signals,
* essentially removing a linear trend from signals, calculated individually for
* each EEG channel
*
* @param x a pointer to an array containing EEG signals from different channels,
* channel n data should start at position x[n_chans * n_time_steps],
* total length of x array should be n_chans * n_time_steps
* @param n_chans number of recording channels
* @param n_time_steps number of time samples in each channel recording
* @param x_detrend a pointer to an array which returns detrended EEG signals,
* its length is the same as x
*/
BA_BCICONNECT_DLL_EXPORT void ba_bci_connect_detrend(double* x, const size_t n_chans, const size_t n_time_steps, double* x_detrend) NOEXCEPT;

/**
 * @brief Calcultates the means of EEG signals
 *
 * @details This function calculates the means of EEG signals. 
 *
 * @param x a pointer to an array containing EEG signals from different channels,
 * channel n data should start at position x[n_chans * n_time_steps],
 * total length of x array should be n_chans * n_time_steps
 * @param n_chans number of recording channels
 * @param n_time_steps number of time samples in each channel recording
 * @param mean a pointer to an array which returns the mean of each channel,
 * its length should be n_chans
 */
BA_BCICONNECT_DLL_EXPORT void ba_bci_connect_mean(const double* x, size_t n_chans, size_t n_time_steps, double* mean) NOEXCEPT;

/**
 * @brief Calcultates the standard deviation of EEG signals
 *
 * @details This function calculates the standard deviation of EEG signals.
 *
 * @param x a pointer to an array containing EEG signals from different channels,
 * channel n data should start at position x[n_chans * n_time_steps],
 * total length of x array should be n_chans * n_time_steps
 * @param n_chans number of recording channels
 * @param n_time_steps number of time samples in each channel recording
 * @param std a pointer to an array which returns the standard deviation of each channel,
 * its length should be n_chans
 */
BA_BCICONNECT_DLL_EXPORT void ba_bci_connect_std(const double* x, size_t n_chans, size_t n_time_steps, double* std) NOEXCEPT;

/**
 * @brief Calcultates the median of EEG signals
 *
 * @details This function calculates the median of EEG signals.
 *
 * @param x a pointer to an array containing EEG signals from different channels,
 * channel n data should start at position x[n_chans * n_time_steps],
 * total length of x array should be n_chans * n_time_steps
 * @param n_chans number of recording channels
 * @param n_time_steps number of time samples in each channel recording
 * @param median a pointer to an array which returns the median of each channel,
 * its length should be n_chans
 */
BA_BCICONNECT_DLL_EXPORT void ba_bci_connect_median(double* x, const size_t n_chans, const size_t n_time_steps, double* median) NOEXCEPT;

/**
 * @brief Calcultates the median absolute deviation of EEG signals
 *
 * @details This function calculates the meadian absolute deviation of EEG signals.
 *
 * @param x a pointer to an array containing EEG signals from different channels,
 * channel n data should start at position x[n_chans * n_time_steps],
 * total length of x array should be n_chans * n_time_steps
 * @param n_chans number of recording channels
 * @param n_time_steps number of time samples in each channel recording
 * @param mad a pointer to an array which returns the meadian absolute deviation of each channel,
 * its length should be n_chans
 */
BA_BCICONNECT_DLL_EXPORT void ba_bci_connect_mad(double* x, const size_t n_chans, const size_t n_time_steps, double* mad) NOEXCEPT;

/**
 * @brief Subtracts the mean from EEG signals
 *
 * @details This function subtracts the mean from EEG signals, 
 * essentially removing the DC offset in the EEG recordings
 *
 * @param x a pointer to an array containing EEG signals from different channels,
 * channel n data should start at position x[n_chans * n_time_steps],
 * total length of x array should be n_chans * n_time_steps
 * @param n_chans number of recording channels
 * @param n_time_steps number of time samples in each channel recording
 * @param x_demean a pointer to an array which returns EEG signals with subtracted mean,
 * its length is the same as x
 */
BA_BCICONNECT_DLL_EXPORT void ba_bci_connect_demean(const double* x, size_t n_chans, size_t n_time_steps, double* x_demean) NOEXCEPT;

/**
 * @brief Standardizes the provided EEG signals
 *
 * @details This function standardizes the provided EEG signals,
 * essentially making the mean of the signals equal to zero and standard deviation to one.
 *
 * @param x a pointer to an array containing EEG signals from different channels,
 * channel n data should start at position x[n_chans * n_time_steps],
 * total length of x array should be n_chans * n_time_steps
 * @param n_chans number of recording channels
 * @param n_time_steps number of time samples in each channel recording
 * @param x_standard a pointer to an array which returns standardized EEG signals,
 * its length is the same as x
 */
BA_BCICONNECT_DLL_EXPORT void ba_bci_connect_standartize(const double* x, size_t n_chans, size_t n_time_steps, double* x_standard) NOEXCEPT;

/**
 * @brief Calculates exponential weigted moving average of EEG signals
 *
 * @details This function calculates exponential weighted moving average of EEG signals
 *
 * @param x a pointer to an array containing EEG signals from different channels,
 * channel n data should start at position x[n_chans * n_time_steps],
 * total length of x array should be n_chans * n_time_steps
 * @param n_chans number of recording channels
 * @param n_time_steps number of time samples in each channel data
 * @param ewma a pointer to an array which returns the calculated average for each channel,
 * its length should be n_chans
 */
BA_BCICONNECT_DLL_EXPORT void ba_bci_connect_ewma(const double* x, size_t n_chans, size_t n_time_steps, double alpha, double* ewma) NOEXCEPT;

/**
 * @brief Standardizes the provided EEG signals using exponential weighted moving average
 *
 * @details This function standardizes the provided EEG signals using exponential weighted moving average
 *
 * @param x a pointer to an array containing EEG signals from different channels,
 * channel n data should start at position x[n_chans * n_time_steps],
 * total length of x array should be n_chans * n_time_steps
 * @param n_chans number of recording channels
 * @param n_time_steps number of time samples in each channel data
 * @param alpha smoothing factor, in braindecode alpha = 0.001
 * @param epsilon stabilizer for division by zero variance, in braindecode epsilon = 1e-4
 * @param x_standard a pointer to an array which returns standardized EEG signals,
 * its length should be the same as x
 */
BA_BCICONNECT_DLL_EXPORT void ba_bci_connect_ewma_standartize(const double* x, size_t n_chans, size_t n_time_steps, double alpha, double epsilon, double* x_standard) NOEXCEPT;

/**
 * @brief Lowpass filtering of the provided EEG signals
 *
 * @details This function lowpass filters the provided EEG signals using 5th order Butterworth filter,
 * phase is corrected for zero lag
 *
 * @param x a pointer to an array containing EEG signals from different channels,
 * channel n data should start at position x[n_chans * n_time_steps],
 * total length of x array should be n_chans * n_time_steps,
 * the array data is replaced with filtered signals, so the user is responsible in making a copy
 * of original EEG signals if needed
 * @param n_chans number of recording channels
 * @param n_time_steps number of time samples in each channel data
 * @param sampling frequency of EEG signals
 * @param cutoff_freq cutoff frequency of low pass filter
 */
BA_BCICONNECT_DLL_EXPORT void ba_bci_connect_filter_lowpass(double* x, size_t n_chans, size_t n_time_steps, double sampling_freq, double cutoff_freq) NOEXCEPT;

/**
 * @brief Highpass filtering of the provided EEG signals
 *
 * @details This function highpass filters the provided EEG signals using 5th order Butterworth filter,
 * phase is corrected for zero lag
 *
 * @param x a pointer to an array containing EEG signals from different channels,
 * channel n data should start at position x[n_chans * n_time_steps],
 * total length of x array should be n_chans * n_time_steps,
 * the array data is replaced with filtered signals, so the user is responsible in making a copy
 * of original EEG signals if needed
 * @param n_chans number of recording channels
 * @param n_time_steps number of time samples in each channel data
 * @param sampling frequency of EEG signals
 * @param cutoff_freq cutoff frequency of highpass filter
 */
BA_BCICONNECT_DLL_EXPORT void ba_bci_connect_filter_highpass(double* x, size_t n_chans, size_t n_time_steps, double sampling_freq, double cutoff_freq) NOEXCEPT;

/**
 * @brief Bandpass filtering of the provided EEG signals
 *
 * @details This function bandpass filters the provided EEG signals using 4th order Butterworth filter,
 * phase is corrected for zero lag
 *
 * @param x a pointer to an array containing EEG signals from different channels,
 * channel n data should start at position x[n_chans * n_time_steps],
 * total length of x array should be n_chans * n_time_steps,
 * the array data is replaced with filtered signals, so the user is responsible in making a copy
 * of original EEG signals if needed
 * @param n_chans number of recording channels
 * @param n_time_steps number of time samples in each channel data
 * @param sampling frequency of EEG signals
 * @param low_freq the low cutoff frequency
 * @param high_freq the high cutoff frequency
 */
BA_BCICONNECT_DLL_EXPORT void ba_bci_connect_filter_bandpass(double* x, size_t n_chans, size_t n_time_steps, double sampling_freq, double low_freq, double high_freq) NOEXCEPT;

/**
 * @brief Notch filtering of the provided EEG signals
 *
 * @details This function notch filters the provided EEG signals using 4th order Butterworth filter,
 * phase is corrected for zero lag
 *
 * @param x a pointer to an array containing EEG signals from different channels,
 * channel n data should start at position x[n_chans * n_time_steps],
 * total length of x array should be n_chans * n_time_steps,
 * the array data is replaced with filtered signals, so the user is responsible in making a copy
 * of original EEG signals if needed
 * @param n_chans number of recording channels
 * @param n_time_steps number of time samples in each channel data
 * @param sampling frequency of EEG signals
 * @param center_freq the center frequency of the notch filter
 * @param width_freq the width of the filter,
 * the filter cutoff frequencies are essentially centre_freq -/+ width_freq/2
 */
BA_BCICONNECT_DLL_EXPORT void ba_bci_connect_filter_notch(double* x, size_t n_chans, size_t n_time_steps, double sampling_freq, double center_freq, double width_freq) NOEXCEPT;

/**
 * @brief Calculates FFT of the provided EEG signals
 *
 * @details This function calculates FFT of the provided EEG signals.
 *
 * @param x array containing EEG signals from different channels,
 * channel n data should start at position x[n_chans * n_time_steps],
 * total length of x array should be n_chans * n_time_steps,
 * @param n_chans Number of recording channels
 * @param n_time_steps Number of samples in each channel
 * @param sampling_freq Frequency of EEG signals
 * @param magnitudes Magnitudes output from FFT result. Must be of length
 * `n_chans * ((n_time_steps - (n_time_steps % 2)) / 2 + 1)`
 * @param phases Phases output from FFT result, in radians. Must be of length
 * `n_chans * ((n_time_steps - (n_time_steps % 2)) / 2 + 1)`
 */
BA_BCICONNECT_DLL_EXPORT void ba_bci_connect_fft(const double* x, size_t n_chans, size_t n_time_steps, double sampling_freq, double* magnitudes, double* phases) NOEXCEPT;

/**
 * @brief Calculates the min and max values of EEG signals
 *
 * @details This function calculates min and max values of each EEG channel signal
 *
 * @param x a pointer to an array containing EEG signals from different channels,
 * channel n data should start at position x[n_chans * n_time_steps],
 * total length of x array should be n_chans * n_time_steps
 * @param n_chans number of recording channels
 * @param n_time_steps number of time samples in each channel recording
 * @param x_min a pointer to an array which returns the min value calculated for each channel
 * @param x_max a pointer to an array which returns the max value calculated for each channel
 */
BA_BCICONNECT_DLL_EXPORT void ba_bci_connect_minmax(double* x, const size_t n_chans, const size_t n_time_steps, double* x_min, double* x_max) NOEXCEPT;

#ifdef __cplusplus
}
#endif
