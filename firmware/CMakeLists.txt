# Top-level ESP-IDF project file
cmake_minimum_required(VERSION 3.16)

# esp-sr ships model data; the model partition is populated from these models.
set(EXTRA_COMPONENT_DIRS "")

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(cj2_voice_checklist)
