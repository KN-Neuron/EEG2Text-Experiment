from src.run import run

DO_USE_DEBUG_MODE = False
DO_USE_MOCK_HEADSET = False

BRAINACCESS_CAP_NAME = "BA MAXI 009"


if __name__ == "__main__":
    run(
        brainaccess_cap_name=BRAINACCESS_CAP_NAME,
        do_use_debug_mode=DO_USE_DEBUG_MODE,
        do_use_mock_headset=DO_USE_MOCK_HEADSET,
    )
