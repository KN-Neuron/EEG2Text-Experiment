// This is the main file for a Bluetooth EEG system application, connection example.
// It includes necessary headers, defines sleep functions, and initializes
// variables.

#include "bacore.h"
#include "eeg_manager.h"
#include <stdio.h>
#include <string.h>

#define DEVICE_NAME "BA MINI 000"
ba_eeg_manager* manager1;
ba_error compatibility;

// Callback function for handling disconnection events.
// This function is called when the connection to the device is lost.
// It prints a message indicating the disconnection event.
void disconnect_callback(void* data)
{
	printf("Disconnectedd\n");
}

// Function to scan for available Bluetooth EEG devices and initialize the
// system.
ba_init_error scan_devices()
{
	// Initialize the status variable to hold the result of the initialization
	ba_init_error status = BA_INIT_ERROR_OK;
	const ba_version* curr_version = ba_core_get_version();
	printf("Core current version : %d.%d.%d\n", curr_version->major, curr_version->minor, curr_version->patch);

	// Initialize the Bluetooth EEG system using the defined version
	status |= ba_core_init();

	// Check if the initialization was successful
	if (status != BA_INIT_ERROR_OK)
	{
		// Print an error message if the initialization failed
		printf("Core init Error: %d\n", status);
		return status;
	}

	// Scan for available Bluetooth EEG devices
	status |= ba_core_scan(0);

	// Check if no devices were found after the first scan
	if (ba_core_device_count() == 0)
	{
		// Keep scanning for devices until at least one is found
		for (int i = 0; i < 5; i++)
		{
			// Print the number of scan attempts
			printf("Found devices count: %d\n", ba_core_device_count());

			// Scan for available devices again
			status |= ba_core_scan(0);
			if (ba_core_device_count() != 0)
			{
				break;
			}
		}
	}

	// Print a message indicating the end of the scanning process
	printf("Search: \n");

	// Check if no devices were found after scanning
	if (ba_core_device_count() == 0)
	{
		// Print a message indicating that no devices were found
		printf("0 Devices were found\n");

		// Close the Bluetooth EEG system
		ba_core_close();

		// Return an error code indicating that no devices were found
		status |= BA_INIT_ERROR_NOT_FOUND;
	}
	return status;
}

// Function to connect to the Bluetooth EEG device and perform EEG operations
ba_init_error connect_ble(ba_eeg_manager** const manager, const char* device_name)
{
	ba_init_error status = BA_INIT_ERROR_OK;

	// Print the number of available devices
	printf("devices found: %d\n", ba_core_device_count());

	// Get the name of the first device
	char name[20];

	// Find the device with the name "BA MINI 002"
	int device = -1;
	for (int i = 0; i < ba_core_device_count(); ++i)
	{
		ba_core_device_get_name(name, i);
		if (strcmp(name, device_name) == 0)
		{
			device = i;
			printf("Device found!!!!!!!\n");
		}
	}

	// If the device is not found, return -1
	if (device < 0)
	{
		return -1;
	}

	// Define the callback function for handling disconnection events
	ba_callback_disconnect disconnect_cb = disconnect_callback;
	// Set the callback function for handling disconnection events
	ba_eeg_manager_set_callback_disconnect(*manager, disconnect_cb, NULL);
	// Connect to the selected device

	compatibility = ba_eeg_manager_connect(*manager, device, NULL, NULL);
	printf("Connected\n");
	printf("device info: %zu\n", ba_eeg_manager_get_device_info(manager)->serial_number);

	const ba_battery_info info = ba_eeg_manager_get_battery_info(*manager);
	printf("battery level: %d | is charger connected: %d | is charging: %d \n", info.level, info.is_charger_connected, info.is_charging);

	// Return the status of the initialization
	return status;
}

// Function to stop the Bluetooth EEG system and disconnect from the device
void disconnect_ble(ba_eeg_manager** const manager)
{
	// Free the EEG manager instance
	ba_eeg_manager_free(*manager);
}

// Main function to run the Bluetooth EEG system application
int main()
{
	scan_devices();

	manager1 = ba_eeg_manager_new();

	uint8_t status = connect_ble(&manager1, DEVICE_NAME);
	if (status != BA_ERROR_OK)
	{
		printf("Error connecting to device: %d\n", status);
		return status;
	}

	disconnect_ble(&manager1);

	// Close the Bluetooth EEG system
	ba_core_close();
	return 0;
}