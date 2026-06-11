/*
 * annunciator.c — drive the Applied Avionics split-legend switch via DIO.
 *
 * TOP half  = LEGEND_OFF_GPIO   (white "VOICE CHKLST OFF")
 * BOTTOM half= LEGEND_FAULT_GPIO (amber "VOICE CHKLST FAULT")
 *
 * Dark-cockpit logic lives in annunciator_update(); the bare set() lets the
 * lamp test and explicit transitions drive the halves directly.
 */
#include "annunciator.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "board_pins.h"

static void cfg_out(int gpio) {
    if (gpio < 0) return;
    gpio_config_t io = { .pin_bit_mask = 1ULL << gpio, .mode = GPIO_MODE_OUTPUT };
    gpio_config(&io);
}

static void off_lamp(bool on) {
#if LEGEND_OFF_GPIO >= 0
    gpio_set_level(LEGEND_OFF_GPIO, on ? LEGEND_OFF_ACTIVE_HIGH : !LEGEND_OFF_ACTIVE_HIGH);
#endif
}

static void fault_lamp(bool on) {
#if LEGEND_FAULT_GPIO >= 0
    gpio_set_level(LEGEND_FAULT_GPIO, on ? LEGEND_FAULT_ACTIVE_HIGH : !LEGEND_FAULT_ACTIVE_HIGH);
#endif
}

void annunciator_set(ann_state_t s) {
    switch (s) {
        case ANN_OFF:   off_lamp(true);  fault_lamp(false); break;  /* white OFF  */
        case ANN_FAULT: off_lamp(false); fault_lamp(true);  break;  /* amber FAULT*/
        case ANN_DARK:
        default:        off_lamp(false); fault_lamp(false); break;  /* dark       */
    }
}

void annunciator_update(bool selected_in, bool fault) {
    if (!selected_in)      annunciator_set(ANN_OFF);    /* OUT inhibits fault (AC 25-11) */
    else if (fault)        annunciator_set(ANN_FAULT);  /* IN + fault                    */
    else                   annunciator_set(ANN_DARK);   /* IN + healthy: dark cockpit    */
}

void annunciator_set_ready(bool ready) {
#if STATUS_LED_GPIO >= 0
    gpio_set_level(STATUS_LED_GPIO, ready ? STATUS_LED_ACTIVE_HIGH : !STATUS_LED_ACTIVE_HIGH);
#endif
}

void annunciator_init(void) {
    cfg_out(LEGEND_OFF_GPIO);
    cfg_out(LEGEND_FAULT_GPIO);
    cfg_out(STATUS_LED_GPIO);

    /* Power-up LAMP TEST: drive both legend halves so a dead LED cannot be
     * mistaken for a healthy dark state, then go dark. */
    off_lamp(true);
    fault_lamp(true);
    annunciator_set_ready(false);
    vTaskDelay(pdMS_TO_TICKS(LAMP_TEST_MS));
    annunciator_set(ANN_DARK);
}
