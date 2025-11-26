# Use Ubuntu as base image
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    sudo \
    bluetooth \
    bluez \
    libbluetooth-dev \
    libglib2.0-dev \
    libasound-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportaudio2 \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Update PATH to include Poetry
ENV PATH="/root/.local/bin:$PATH"

# Create a non-root user
RUN useradd -m -s /bin/bash researcher && \
    usermod -a -G bluetooth researcher

# Set up the working directory
WORKDIR /home/researcher

# Copy the project files (you would copy these in a real Docker setup)
# This is a template - normally you'd copy from your local directory
RUN mkdir -p EEG2Text-Experiment/experiment

# Switch to the researcher user
USER researcher

# Create a script to handle first-time setup
RUN echo '#!/bin/bash\n\
\n\
set -e\n\
\n\
echo "Setting up EEG2Text Experiment..."\n\
\n\
if [ ! -d "EEG2Text-Experiment/experiment" ]; then\n\
  echo "Error: EEG2Text Experiment not found in the expected location."\n\
  echo "Please make sure to mount your project directory properly."\n\
  echo "Example: docker run -v /path/to/your/project:/home/researcher/EEG2Text-Experiment ..."\n\
  exit 1\n\
fi\n\
\n\
cd EEG2Text-Experiment/experiment\n\
\n\
# Install Python dependencies via Poetry\n\
poetry install\n\
\n\
echo "Setup complete! You can now run the experiment with one of these commands:"\n\
echo "  - For real EEG:  bash run_experiment.sh"\n\
echo "  - For mock EEG:  bash run_experiment.sh --mock-eeg"\n\
' > setup_docker.sh

RUN chmod +x setup_docker.sh

# Provide instructions
RUN echo '#!/bin/bash\n\
\n\
echo "EEG2Text Experiment Docker Environment"\n\
echo "====================================="\n\
echo ""\n\
echo "To use this container:"\n\
echo "1. First run setup: docker exec -it <container_name> ./setup_docker.sh"\n\
echo "2. Then run the experiment:\n\
echo "   - Real EEG: docker exec -it <container_name> bash run_experiment.sh\n\
echo "   - Mock EEG: docker exec -it <container_name> bash run_experiment.sh --mock-eeg\n\
echo ""\n\
echo "To run with direct access to the host system:"\n\
echo "docker run -it --privileged --net=host -v /path/to/project:/home/researcher/EEG2Text-Experiment eeg-experiment"\n\
' > README_CONTAINER.md

# Set default command
CMD ["/bin/bash"]