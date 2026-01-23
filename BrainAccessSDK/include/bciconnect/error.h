#pragma once

#include <stdint.h>

typedef uint8_t ba_bci_connect_error;

#define BA_BCI_CONNECT_ERROR_OK 0
#define BA_BCI_CONNECT_ERROR_UNKNOWN -1
#define BA_BCI_CONNECT_ERROR_MODEL_LOAD_FAILED 1
#define BA_BCI_CONNECT_ERROR_NOT_ALLOWED_MODEL_NUMBER 2
