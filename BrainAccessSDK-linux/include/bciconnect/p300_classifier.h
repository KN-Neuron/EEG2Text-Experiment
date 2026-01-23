/**
 * @file p300_classifier.h
 * @author Neurotechnology (brainaccess@neurotechnology.com)
 * @brief P300 classifier
 *
 * @copyright Copyright (c) 2022 Neurotechnology
 */

#pragma once

#include <stdint.h>
#include "dllexport.h"
#include "noexcept.h"
#include "error.h"


#ifdef __cplusplus
extern "C"
{
#endif

/**
 * @brief Initializes neural network model for P300
 *
 * @details This function initializes the P300 model, which can be selected from a model zoo.
 * Models differ in the required number EEG electrode placements, number of repetitions and interstimuli time.
 *
 * @param p Pointer to P300 model instance
 * 
 * @param Model number from a model zoo, currently available options are:
 * 0 - 8 electrode Standard Kit setup, 3 repetitions
 * 1 - 8 electrode Standard Kit setup, 1 repetition
 * 2 - 8 electrode Standard Kit setup, 3 repetitions, "fast" - time between start of subsequent stimuli is 215ms
 * 3 - O1 and O2 electrodes only, 3 repetitions, "fast" - time between start of subsequent stimuli is 215ms
 * 
 * @return Error code
 */
BA_BCICONNECT_DLL_EXPORT ba_bci_connect_error ba_bci_connect_p300_init(void** const p, const uint8_t model_number) NOEXCEPT;

/**
 * @brief Predicts the probability of EEG signals containing P300 potential.
 *
 * @details This function predicts the score of signal containing P300 potential.
 * 
 * @param A pointer to an array containing EEG signals with dimensions number of channels * repetitions * no of samples (176).
 * The data in the array should be arranged in such a manner [Channel0_1st_repetition, Channel0_2repetition, ..., Channel1_1st_repetition, Channel1_2repetition ...]
 * 
 * 
 * @param A pointer to a result that reflects the probability of signal having P300 potential.
 * 
 * @return Error code
 */
BA_BCICONNECT_DLL_EXPORT ba_bci_connect_error ba_bci_connect_p300_predict(void* const p, const double* const measurements, double* const result) NOEXCEPT;

/**
 * @brief Deletes a P300 instance
 *
 * @details Call exactly once to avoid undefined behavior and memory leaks
 * 
 * @param p P300 instance to destroy
 */
BA_BCICONNECT_DLL_EXPORT ba_bci_connect_error ba_bci_connect_p300_free(void* const p) NOEXCEPT;

#ifdef __cplusplus
}
#endif
