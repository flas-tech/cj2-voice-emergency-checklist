// CITATION CJ2 (CE 525A) SN 0001 & Subs — Emergency Checklists
// Source: aircraft emergency checklist card (user-provided).
//
// Data model:
//   id        : machine key
//   title     : display name
//   triggers  : spoken phrases that select this checklist
//   note      : optional condition / context shown under the title
//   items[]   : ordered steps
//       read    : text spoken aloud + displayed
//       action  : the bold "target state" (e.g. IDLE, PUSH)
//       advance : array of completion words that move to the next item
//                 (universal fallbacks "check","checked","complete","next","done"
//                  are added automatically at runtime)
//
// DEMO / TRAINING USE ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS.

const CHECKLISTS = [
  {
    id: "engine_fail_fire_takeoff_below_v1",
    title: "Engine Failure / Fire / Master Warning During Takeoff — Speed Below V1 (Takeoff Rejected)",
    triggers: ["takeoff rejected", "speed below v one", "abort takeoff", "rejected takeoff", "engine failure during takeoff"],
    items: [
      { read: "Brakes — as required", action: "AS REQUIRED", advance: ["as required", "required"] },
      { read: "Throttles — idle", action: "IDLE", advance: ["idle"] },
      { read: "Speed brakes — extend", action: "EXTEND", advance: ["extend", "extended"] }
    ]
  },
  {
    id: "engine_fail_takeoff_above_v1",
    title: "Engine Failure / Fire During Takeoff — Speed Above V1 (Takeoff Continued)",
    triggers: ["takeoff continued", "speed above v one", "continue takeoff", "engine failure above v one"],
    items: [
      { read: "Maintain directional control", action: "", advance: ["maintaining", "maintained", "control"] },
      { read: "Accelerate to V R", action: "VR", advance: ["accelerating", "v r", "rotate speed"] },
      { read: "Rotate at V R, climb at V 2", action: "", advance: ["rotate", "rotating", "climbing"] },
      { read: "Landing gear — up, after positive rate of climb", action: "UP", advance: ["up", "gear up"] },
      { read: "Wing engine crossflow switch — wing crossflow, if wing or engine anti-ice are in wing or engine", action: "WINGX FLOW", advance: ["wing crossflow", "crossflow", "set"] },
      { read: "At 1500 feet A G L, retract flaps at V 2 plus 10, then accelerate to V enroute", action: "", advance: ["flaps up", "retracted", "accelerating"] }
    ]
  },
  {
    id: "engine_fail_final_approach",
    title: "Engine Failure During Final Approach",
    triggers: ["engine failure final approach", "engine failure during final approach", "engine failure approach"],
    items: [
      { read: "Thrust, operating engine — increase as required", action: "INCREASE as required", advance: ["increased", "as required", "set"] },
      { read: "Airspeed — V approach", action: "VAPP", advance: ["v approach", "set", "airspeed set"] },
      { read: "Flaps — takeoff and approach", action: "TAKEOFF AND APPROACH", advance: ["takeoff and approach", "set", "flaps set"] }
    ]
  },
  {
    id: "engine_fire",
    title: "Engine Fire (LH or RH Engine Fire Warning Light Illuminated)",
    triggers: ["engine fire", "fire warning", "engine fire warning"],
    items: [
      { read: "Throttle, affected engine — idle", action: "IDLE", advance: ["idle"] },
      { read: "Engine fire button — lift cover and push", action: "LIFT COVER and PUSH", advance: ["push", "pushed", "lifted and pushed"] },
      { read: "Either illuminated bottle armed button — push", action: "PUSH", advance: ["push", "pushed", "armed"] }
    ]
  },
  {
    id: "emergency_restart_two_engines",
    title: "Emergency Restart — Two Engines",
    triggers: ["emergency restart", "engine restart", "restart engines", "two engine restart"],
    items: [
      { read: "Ignition switches — both on", action: "BOTH ON", advance: ["both on", "on"] },
      { read: "Left and right fuel boost switches — both on", action: "BOTH ON", advance: ["both on", "on"] },
      { read: "Throttles — idle", action: "IDLE", advance: ["idle"] },
      { read: "If altitude allows — increase airspeed to 200 knots", action: "INCREASE AIRSPEED TO 200 KIAS", advance: ["two hundred", "increased", "set"] }
    ]
  },
  {
    id: "electrical_fire_smoke",
    title: "Electrical Fire or Smoke & Environmental System Smoke or Odor & Smoke Removal",
    triggers: ["electrical fire", "electrical smoke", "smoke or odor", "smoke removal", "cabin smoke", "electrical fire or smoke"],
    items: [
      { read: "Oxygen masks — don and emergency", action: "DON and EMER", advance: ["on", "donned", "emergency"] },
      { read: "Microphone select switches — mic oxygen mask", action: "MIC OXY MASK", advance: ["set", "oxygen mask", "selected"] }
    ]
  },
  {
    id: "cabin_altitude",
    title: "Cabin Altitude (CABIN ALT)",
    triggers: ["cabin altitude", "cabin alt", "cabin pressure", "depressurization"],
    items: [
      { read: "Oxygen masks — don and 100 percent oxygen", action: "DON and 100% OXYGEN", advance: ["on", "donned", "one hundred percent"] },
      { read: "Microphone select switches — mic oxygen mask", action: "MIC OXY MASK", advance: ["set", "oxygen mask", "selected"] },
      { read: "Emergency descent — as required", action: "AS REQUIRED", advance: ["as required", "required", "descending"] },
      { read: "Passenger oxygen — make sure passengers are receiving oxygen", action: "MAKE SURE passengers are receiving oxygen", advance: ["confirmed", "receiving", "set"] }
    ]
  },
  {
    id: "emergency_descent",
    title: "Emergency Descent",
    triggers: ["emergency descent", "rapid descent", "emergency descend"],
    items: [
      { read: "Autopilot trim disconnect button — press and release", action: "PRESS and RELEASE", advance: ["pressed", "released", "press and release"] },
      { read: "Throttles — idle", action: "IDLE", advance: ["idle"] },
      { read: "Speed brakes — extend", action: "EXTEND", advance: ["extend", "extended"] },
      { read: "Airplane pitch attitude — approximately 20 degrees nose down", action: "APPROXIMATELY 20 DEGREES NOSE DOWN", advance: ["nose down", "set", "twenty degrees"] }
    ]
  },
  {
    id: "battery_overtemp",
    title: "BATT O'TEMP (Battery Overtemperature)",
    triggers: ["battery overtemp", "battery overtemperature", "batt o temp", "battery over temperature"],
    items: [
      { read: "Volt amp — note", action: "NOTE", advance: ["noted", "note"] },
      { read: "Battery switch — emergency", action: "EMER", advance: ["emergency", "set"] },
      { read: "Volt amp — note decrease", action: "NOTE DECREASE", advance: ["noted", "decreasing", "note decrease"] }
    ]
  },
  {
    id: "autopilot_malfunction",
    title: "Autopilot Malfunction",
    triggers: ["autopilot malfunction", "autopilot failure", "autopilot runaway"],
    items: [
      { read: "Autopilot trim disconnect button — press and release", action: "PRESS AND RELEASE", advance: ["pressed", "released", "press and release"] }
    ]
  },
  {
    id: "electric_elevator_trim_runaway",
    title: "Electric Elevator Trim Runaway",
    triggers: ["elevator trim runaway", "electric trim runaway", "trim runaway", "elevator trim"],
    items: [
      { read: "Autopilot trim disconnect button — press and release", action: "PRESS AND RELEASE", advance: ["pressed", "released", "press and release"] },
      { read: "Throttles — as required", action: "AS REQUIRED", advance: ["as required", "required", "set"] },
      { read: "Speed brakes — as required", action: "AS REQUIRED", advance: ["as required", "required", "set"] },
      { read: "Manual elevator trim — as required", action: "AS REQUIRED", advance: ["as required", "required", "set"] },
      { read: "Pitch trim circuit breaker, left panel — pull", action: "PULL", advance: ["pull", "pulled"] }
    ]
  },
  {
    id: "emergency_evacuation",
    title: "Emergency Evacuation",
    triggers: ["emergency evacuation", "evacuate", "evacuation"],
    items: [
      { read: "Parking brake — set", action: "SET", advance: ["set"] },
      { read: "Throttles — both off", action: "BOTH OFF", advance: ["both off", "off"] },
      { read: "Left and right engine fire buttons — both press", action: "BOTH PRESS", advance: ["both press", "pressed", "press"] },
      { read: "Illuminated bottle armed buttons — both press, if fire suspected", action: "BOTH PRESS", advance: ["both press", "pressed", "press"] },
      { read: "Battery switch — off", action: "OFF", advance: ["off"] },
      { read: "Emergency Locator Transmitter, E L T — make sure system is activated, if required for search and rescue services", action: "MAKE SURE SYSTEM IS ACTIVATED", advance: ["activated", "confirmed", "set"] },
      { read: "Airplane and immediate area — check for best escape route", action: "CHECK FOR BEST ESCAPE ROUTE", advance: ["checked", "route selected", "confirmed"] },
      // Branch point — read aloud as a decision
      { read: "Decision: if exiting through the cabin door, say cabin door. If exiting through the emergency exit, say emergency exit.", action: "BRANCH", advance: ["cabin door", "emergency exit"],
        branch: { "cabin door": "branch_cabin_door", "emergency exit": "branch_emergency_exit" } }
    ],
    branches: {
      branch_cabin_door: [
        { read: "Cabin door — open", action: "OPEN", advance: ["open", "opened"] },
        { read: "Move away from airplane. Procedure complete.", action: "", advance: ["clear", "complete", "moving away"] }
      ],
      branch_emergency_exit: [
        { read: "Emergency exit door — remove and throw exit door out of the aircraft", action: "REMOVE AND THROW", advance: ["removed", "thrown", "clear"] },
        { read: "Move away from airplane. Procedure complete.", action: "", advance: ["clear", "complete", "moving away"] }
      ]
    }
  }
];

// Universal advance words accepted on any item in addition to item-specific ones.
const UNIVERSAL_ADVANCE = ["check", "checked", "complete", "completed", "next", "done", "continue"];

if (typeof module !== "undefined") { module.exports = { CHECKLISTS, UNIVERSAL_ADVANCE }; }
