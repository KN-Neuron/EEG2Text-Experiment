/**
 * @file ssvep_classifier.h
 * @author Neurotechnology (brainaccess@neurotechnology.com)
 * @brief SSVEP classifier
 *
 * @copyright Copyright (c) 2022 Neurotechnology
 */

#pragma once

#include "dllexport.h"
#include "noexcept.h"
#include <stdlib.h>

#ifdef __cplusplus
extern "C"
{
#endif

/**
 * @brief Classifies EEG SSVEP (steady state visually evoked potentials).
 *
 * @details Classifies EEG SSVEP (steady state visually evoked potentials) into a
 * given set of class frequencies.
 *
 * @param x a pointer to an array containing EEG signals from different channels,
 * channel n data should statrt at position x[n_chans*n_time_steps],
 * total length of x array should be n_chans*n_time_steps
 * @param n_time_steps number of time samples in each channel recording
 * @param n_chans number of recording channels
 * @param sampling_rate sampling rate in hertz.
 * @param freqs a pointer to frequency class array.
 * @param n_classes a number of frequency classes.
 * @param score address where classification score will be stored.
 * @return Best matching class, selected from given frequency class array.
 */
BA_BCICONNECT_DLL_EXPORT size_t ba_bci_connect_ssvep_classify(const double* x, size_t n_time_steps, size_t n_chans, double sampling_rate, const double* freqs, size_t n_classes, double* score) NOEXCEPT;

#ifdef __cplusplus
}
#endif
