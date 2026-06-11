idf_component_register(
    SRCS "main.c" "checklists.c" "audio_player.c" "checklist_store.c" "annunciator.c"
    INCLUDE_DIRS "."
    REQUIRES esp-sr esp_spiffs driver json fatfs sdmmc esp_driver_sdmmc
)

# Flash the audio clips (built by scripts/make_audio.py into ../audio) into a
# SPIFFS image on the 'storage' partition.
spiffs_create_partition_image(storage ${CMAKE_CURRENT_LIST_DIR}/../audio FLASH_IN_PROJECT)
