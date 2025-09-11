import time

import pygame

pygame.mixer.init()
pygame.init()  # Initialize all pygame modules

# Check if mixer initialized properly
if not pygame.mixer.get_init():
    print("Error: Pygame mixer not initialized")
    exit(1)

try:
    # Set volume (0.0 to 1.0)
    pygame.mixer.music.set_volume(0.7)

    # Load and play background music
    pygame.mixer.music.load("./sentence1.mp3")
    pygame.mixer.music.play(-1)  # -1 for looping

    print("Playing audio... Press Ctrl+C to stop")

    # Keep the program running to allow audio to play
    while pygame.mixer.music.get_busy():
        # This loop prevents the script from ending
        # You can also use pygame.time.wait() if you don't need interactivity
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopping audio playback")
except Exception as e:
    print(f"Error: {e}")
finally:
    pygame.mixer.music.stop()
    pygame.quit()
