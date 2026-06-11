/*
 * annunciator.h — Applied Avionics split-legend annunciator switch.
 *
 * Dark-cockpit philosophy (FAA AC 25-11): nothing is lit when the system is
 * selected IN and healthy. Two independently driven legend halves:
 *   TOP   — white "VOICE CHKLST OFF"  (lit only when selected OUT)
 *   BOTTOM— amber "VOICE CHKLST FAULT" (lit only when selected IN + fault)
 */
#pragma once
#include <stdbool.h>

/* The annunciator's three mutually exclusive display states. */
typedef enum {
    ANN_DARK = 0,   /* selected IN + healthy: both halves dark            */
    ANN_OFF,        /* selected OUT: white OFF legend, fault inhibited     */
    ANN_FAULT       /* selected IN + fault: amber FAULT legend            */
} ann_state_t;

/* Configure GPIOs and run the power-up lamp test (both halves on briefly,
 * then dark). Blocks for LAMP_TEST_MS. */
void annunciator_init(void);

/* Set the displayed state directly. */
void annunciator_set(ann_state_t s);

/* Convenience: resolve the correct legend state from the two inputs and
 * apply it. selected_in = switch IN (system on); fault = a fault exists. */
void annunciator_update(bool selected_in, bool fault);

/* Status light: true = ready/listening (independent of the legend). */
void annunciator_set_ready(bool ready);
