# =============================================================================
# Smarter Traffic Light — Full System
# =============================================================================
# Coordinate system: (0,0) = NW corner
# Intersection boundary: N<340, S>620, W<360, E>690
#
# Traffic lights 1-4:
#   1 = North approach   2 = East approach
#   3 = South approach   4 = West approach
#
# LED array (sent to Arduino):
#   [G1,G2,G3,G4, Y1,Y2,Y3,Y4, R1,R2,R3,R4, P1,P2,P3,P4]
#    0  1  2  3   4  5  6  7   8  9  10 11  12 13 14 15
#
# Pedestrian zones (sidewalk corners, no button needed):
#   Standing near N side  → wants to cross E/W road → stops lights 2 & 4
#   Standing near S side  → wants to cross E/W road → stops lights 2 & 4
#   Standing near W side  → wants to cross N/S road → stops lights 1 & 3
#   Standing near E side  → wants to cross N/S road → stops lights 1 & 3
#
#   Detection zone: outside the intersection box but within ~80px of it,
#   AND outside the car lane bands (on the sidewalk strip)
# =============================================================================

import time

# ── Intersection boundary ─────────────────────────────────────────────────────
NORTH_THRESH = 340
SOUTH_THRESH = 620
WEST_THRESH  = 360
EAST_THRESH  = 690

# How far outside the box a pedestrian can be and still be detected
PED_DETECT_MARGIN = 80

# ── Car lane ranges ───────────────────────────────────────────────────────────
LANE_RANGES = {
    "E": [(400, 470), (480, 540), (550, 670)],   # y-ranges
    "W": [(350, 410), (420, 480), (490, 570)],   # y-ranges
    "N": [(350, 420), (430, 500), (510, 580)],   # x-ranges
    "S": [(450, 520), (530, 590), (600, 670)],   # x-ranges
}

LANE_DIRECTIONS = {
    "E": {1: 1, 2: 2, 3: 3},
    "W": {1: 1, 2: 2, 3: 3},
    "N": {1: 1, 2: 2, 3: 3},
    "S": {1: 1, 2: 2, 3: 3},
}

CONFLICT_MAP = {
    ("E", 1): 1,  ("E", 2): None, ("E", 3): 3,
    ("W", 1): 3,  ("W", 2): None, ("W", 3): 1,
    ("N", 1): 4,  ("N", 2): None, ("N", 3): 2,
    ("S", 1): 2,  ("S", 2): None, ("S", 3): 4,
}

# Pedestrian timing
PED_WARN_TIME  = 3.0   # seconds of yellow warning before red
PED_HOLD_TIME  = 8.0   # seconds of red + walk signal
PED_DWELL_TIME = 1.5   # seconds a pedestrian must be present before triggering
CLEAR_DISTANCE = 60    # px — car must be further than this for ped to cross


# ── Car helpers ───────────────────────────────────────────────────────────────
def get_approach(x, y):
    if y < NORTH_THRESH:   return "N"
    elif y > SOUTH_THRESH: return "S"
    elif x < WEST_THRESH:  return "W"
    elif x > EAST_THRESH:  return "E"
    return None

def get_lane(approach, x, y):
    coord = y if approach in ("E", "W") else x
    for lane_num, (lo, hi) in enumerate(LANE_RANGES[approach], start=1):
        if lo <= coord <= hi:
            return lane_num
    return None

def get_distance(approach, x, y):
    if approach == "N": return NORTH_THRESH - y
    if approach == "S": return y - SOUTH_THRESH
    if approach == "W": return WEST_THRESH - x
    if approach == "E": return x - EAST_THRESH
    return 0


# ── Pedestrian zone detection ─────────────────────────────────────────────────
def get_ped_crossing(x, y):
    """
    Determine which road a pedestrian at (x,y) wants to cross, based purely
    on which sidewalk corner they're standing at.

    Returns the virtual 'button id' (1-4) or None if not in a ped zone.

    Sidewalk zones are the strips just outside the intersection box,
    to the side of (not in) the car lane bands:

      North sidewalk: y in [NORTH_THRESH-margin, NORTH_THRESH),
                      x outside all N lane bands  → crosses E/W road → button 1
      South sidewalk: y in (SOUTH_THRESH, SOUTH_THRESH+margin],
                      x outside all S lane bands  → crosses E/W road → button 3
      West  sidewalk: x in [WEST_THRESH-margin, WEST_THRESH),
                      y outside all W lane bands  → crosses N/S road → button 4
      East  sidewalk: x in (EAST_THRESH, EAST_THRESH+margin],
                      y outside all E lane bands  → crosses N/S road → button 2
    """
    def in_any_lane(approach, coord):
        return any(lo <= coord <= hi for lo, hi in LANE_RANGES[approach])

    # Check x-axis zones (E/W) first to resolve corner ambiguity
    # West sidewalk — pedestrian about to cross North/South road
    if (WEST_THRESH - PED_DETECT_MARGIN) <= x < WEST_THRESH:
        if not in_any_lane("W", y):
            return 4

    # East sidewalk — pedestrian about to cross North/South road
    if EAST_THRESH < x <= (EAST_THRESH + PED_DETECT_MARGIN):
        if not in_any_lane("E", y):
            return 2

    # North sidewalk — pedestrian about to cross East/West road
    if (NORTH_THRESH - PED_DETECT_MARGIN) <= y < NORTH_THRESH:
        if not in_any_lane("N", x):
            return 1

    # South sidewalk — pedestrian about to cross East/West road
    if SOUTH_THRESH < y <= (SOUTH_THRESH + PED_DETECT_MARGIN):
        if not in_any_lane("S", x):
            return 3

    return None

# Which lights each virtual button stops
PED_BUTTON_STOPS = {
    1: [2, 4],   # N sidewalk: cross E/W road → stop E & W lights
    2: [1, 3],   # E sidewalk: cross N/S road → stop N & S lights
    3: [2, 4],   # S sidewalk: cross E/W road → stop E & W lights
    4: [1, 3],   # W sidewalk: cross N/S road → stop N & S lights
}


# ── Data classes ──────────────────────────────────────────────────────────────
class CarBehavior:
    def __init__(self, approach, lane, direction, distance, position, conflict_light):
        self.approach       = approach
        self.lane           = lane
        self.direction      = direction
        self.distance       = distance
        self.position       = position
        self.conflict_light = conflict_light

    def __repr__(self):
        dirs = {1: "LEFT", 2: "STRAIGHT", 3: "RIGHT"}
        return (f"Car(approach={self.approach}, lane={self.lane}, "
                f"dir={dirs[self.direction]}, dist={self.distance:.0f}px, "
                f"conflicts={self.conflict_light})")


class PedRequest:
    def __init__(self, button_id, timestamp):
        self.button_id    = button_id
        self.stops        = PED_BUTTON_STOPS[button_id]
        self.requested_at = timestamp
        self.state        = "warning"    # skip "waiting" — detected = already there
        self.state_since  = timestamp

    def __repr__(self):
        return f"PedRequest(button={self.button_id}, stops={self.stops}, state={self.state})"


# ── Main controller ───────────────────────────────────────────────────────────
class IntersectionController:
    def __init__(self):
        self.ped_requests  = []
        # Track how long each ped zone has been occupied: {button_id: first_seen_time}
        self._ped_dwell    = {}

    def _handle_pedestrian_detections(self, ped_positions):
        """
        Given list of (x,y) pedestrian positions, trigger crossing requests
        after they've been present for PED_DWELL_TIME seconds.
        """
        now = time.time()
        seen_buttons = set()

        for x, y in ped_positions:
            btn = get_ped_crossing(x, y)
            if btn is None:
                continue
            seen_buttons.add(btn)
            already_active = any(r.button_id == btn and r.state != "done"
                                 for r in self.ped_requests)
            if already_active:
                continue

            if btn not in self._ped_dwell:
                self._ped_dwell[btn] = now
            elif now - self._ped_dwell[btn] >= PED_DWELL_TIME:
                self.ped_requests.append(PedRequest(btn, now))
                del self._ped_dwell[btn]
                print(f"[PED] Pedestrian detected at zone {btn} — crossing request raised")

        # Clear dwell timers for zones no longer occupied
        for btn in list(self._ped_dwell.keys()):
            if btn not in seen_buttons:
                del self._ped_dwell[btn]

    def _road_clear_for_ped(self, stops, cars):
        approach_for_light = {1: "N", 2: "E", 3: "S", 4: "W"}
        blocked = {approach_for_light[l] for l in stops}
        return all(car.distance >= CLEAR_DISTANCE
                   for car in cars if car.approach in blocked)

    def update(self, cars, ped_positions=None):
        """
        Args:
            cars          : list of CarBehavior
            ped_positions : list of (x, y) tuples for detected pedestrians

        Returns:
            16-element bool list for Arduino
        """
        now = time.time()

        if ped_positions:
            self._handle_pedestrian_detections(ped_positions)

        # Start from green for all lights
        light_states = {1: "green", 2: "green", 3: "green", 4: "green"}
        ped_signals  = {1: False,   2: False,   3: False,   4: False}

        # ── Car pressure ──────────────────────────────────────────────────────
        YELLOW_DIST = 120
        RED_DIST    = 50
        light_pressure = {1: [], 2: [], 3: [], 4: []}
        approach_to_light = {"N": 1, "E": 2, "S": 3, "W": 4}
        for car in cars:
            light_pressure[approach_to_light[car.approach]].append(car.distance)
            if car.conflict_light:
                light_pressure[car.conflict_light].append(car.distance)

        for idx, distances in light_pressure.items():
            if not distances: continue
            closest = min(distances)
            if closest < RED_DIST:
                light_states[idx] = "red"
            elif closest < YELLOW_DIST and light_states[idx] != "red":
                light_states[idx] = "yellow"

        # ── Pedestrian state machine ──────────────────────────────────────────
        active = []
        for req in self.ped_requests:
            if req.state == "done":
                continue
            elapsed = now - req.state_since

            if req.state == "warning":
                for l in req.stops:
                    if light_states[l] != "red":
                        light_states[l] = "yellow"
                if elapsed >= PED_WARN_TIME:
                    req.state      = "crossing"
                    req.state_since = now
                    print(f"[PED] Zone {req.button_id} — CROSSING now, traffic stopped")

            if req.state == "crossing":
                if elapsed >= PED_HOLD_TIME:
                    req.state = "done"
                    print(f"[PED] Zone {req.button_id} — crossing complete")
                else:
                    for l in req.stops:
                        light_states[l] = "red"
                        ped_signals[l]  = True

            if req.state != "done":
                active.append(req)

        self.ped_requests = active

        return self._build_led_array(light_states, ped_signals)

    def _build_led_array(self, light_states, ped_signals):
        green  = [light_states[i] == "green"  for i in range(1, 5)]
        yellow = [light_states[i] == "yellow" for i in range(1, 5)]
        red    = [light_states[i] == "red"    for i in range(1, 5)]
        ped    = [ped_signals[i]              for i in range(1, 5)]
        return green + yellow + red + ped


# ── Top-level API ─────────────────────────────────────────────────────────────
def classify_object(object_type, position):
    """Returns CarBehavior for cars, None for everything else."""
    if object_type.lower() != "car":
        return None
    x, y    = position
    approach = get_approach(x, y)
    if not approach: return None
    lane = get_lane(approach, x, y)
    if not lane: return None
    direction      = LANE_DIRECTIONS[approach][lane]
    distance       = get_distance(approach, x, y)
    conflict_light = CONFLICT_MAP.get((approach, direction))
    return CarBehavior(approach, lane, direction, distance, position, conflict_light)


_controller = IntersectionController()

def process_frame(detections, ped_positions=None):
    """
    Args:
        detections    : list of (object_type: str, position: (x,y))
        ped_positions : list of (x, y) for detected pedestrians (optional)
    Returns:
        16-element bool list for Arduino
    """
    cars = [classify_object(t, p) for t, p in detections]
    cars = [c for c in cars if c]
    return _controller.update(cars, ped_positions or [])