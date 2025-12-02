import time


class TrolleyController:
    """
    Simple trolley controller.

    Assumptions:
      - train.throttle is in [-1.0 .. 1.0]
      - l_sw_io.value == True when LEFT bumper is hit
      - r_sw_io.value == True when RIGHT bumper is hit
    """

    def __init__(
        self,
        train,
        l_sw_io,
        r_sw_io,
        ramp_start_ratio=0.7,
        min_throttle=0.08,
        off_bumper_time=0.3,
        ramp_steps=3,
    ):
        self.train = train
        self.l_sw_io = l_sw_io
        self.r_sw_io = r_sw_io

        self.ramp_start_ratio = float(ramp_start_ratio)
        self.min_throttle = float(min_throttle)
        self.off_bumper_time = float(off_bumper_time)
        self.ramp_steps = int(ramp_steps)

        self.base_speed = None
        self.time_forward = None   # left -> right
        self.time_reverse = None   # right -> left

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------

    def calibrate(self, speed=0.3, cycles=3):
        """
        Calibrate travel time between bumpers at a fixed speed (NO ramp).

        speed: throttle magnitude (0.0..1.0)
        cycles: how many forward+reverse pairs to measure
        """
        s = float(speed)
        if s <= 0:
            raise ValueError("speed must be > 0")
        if s > 1.0:
            s = 1.0

        self.base_speed = s

        f_times = []
        r_times = []

        for _ in range(cycles):
            # forward leg: left -> right (direction +1)
            t_f = self._leg_constant(direction=+1, speed=s)
            if t_f > 0:
                f_times.append(t_f)
            self._back_off(direction=+1)

            # reverse leg: right -> left (direction -1)
            t_r = self._leg_constant(direction=-1, speed=s)
            if t_r > 0:
                r_times.append(t_r)
            self._back_off(direction=-1)

        f_valid = [t for t in f_times if t > 0]
        r_valid = [t for t in r_times if t > 0]

        if not f_valid or not r_valid:
            raise RuntimeError("Calibration failed: no valid times measured")

        self.time_forward = sum(f_valid) / len(f_valid)
        self.time_reverse = sum(r_valid) / len(r_valid)

        return {
            "base_speed": self.base_speed,
            "time_forward": self.time_forward,
            "time_reverse": self.time_reverse,
        }

    def shuttle(self, start_direction, cycles=None):
        """
        Run back and forth between bumpers with multi-step ramp.

        start_direction:
            +1 = start moving toward RIGHT bumper
            -1 = start moving toward LEFT bumper

        cycles: number of one-way legs; None = run forever.
        """
        if start_direction > 0:
            direction = +1
        elif start_direction < 0:
            direction = -1
        else:
            raise ValueError("start_direction must be +1 or -1")

        if self.base_speed is None or self.time_forward is None or self.time_reverse is None:
            raise RuntimeError("Call calibrate() first")

        # Make sure estimates are sane
        MIN_EST = 0.2
        t_f = max(self.time_forward, MIN_EST)
        t_r = max(self.time_reverse, MIN_EST)

        count = 0
        while True:
            est = t_f if direction > 0 else t_r
            est = max(est, MIN_EST)

            actual = self._leg_ramped(direction, self.base_speed, est)

            # slight smoothing so it self-tunes
            if direction > 0:
                t_f = 0.9 * t_f + 0.1 * actual
            else:
                t_r = 0.9 * t_r + 0.1 * actual

            self._back_off(direction)
            direction *= -1
            count += 1

            if cycles is not None and count >= cycles:
                break

        self.time_forward = t_f
        self.time_reverse = t_r

    # --------------------------------------------------
    # SWITCH HELPERS (True means "hit")
    # --------------------------------------------------

    def _left_hit(self):
        return bool(self.l_sw_io.value)

    def _right_hit(self):
        return bool(self.r_sw_io.value)

    # --------------------------------------------------
    # MOVEMENT HELPERS
    # --------------------------------------------------

    def _back_off(self, direction, mag=None):
        """
        Move away from the last bumper for a fixed time.
        No switch logic here – purely time-based to avoid getting stuck.
        """
        if mag is None:
            mag = self.base_speed if self.base_speed is not None else 0.3
        mag = min(abs(mag), 1.0)

        # Move opposite of the last direction
        self.train.throttle = -direction * mag
        t0 = time.monotonic()
        while time.monotonic() - t0 < self.off_bumper_time:
            time.sleep(0.01)
        self.train.throttle = 0.0

    # --------------------------------------------------
    # LEG LOGIC: CALIBRATION (NO RAMP)
    # --------------------------------------------------

    def _leg_constant(self, direction, speed):
        """
        One leg at constant speed until the corresponding bumper is hit.
        Used during calibration.
        """
        speed = min(abs(speed), 1.0)
        self.train.throttle = direction * speed

        t0 = time.monotonic()
        timeout = 10.0

        while True:
            now = time.monotonic()
            elapsed = now - t0

            if direction > 0 and self._right_hit():
                self.train.throttle = 0.0
                return elapsed
            if direction < 0 and self._left_hit():
                self.train.throttle = 0.0
                return elapsed

            if elapsed > timeout:
                self.train.throttle = 0.0
                raise RuntimeError("Calibration timeout waiting for bumper")

            time.sleep(0.01)

    # --------------------------------------------------
    # LEG LOGIC: SHUTTLE (WITH RAMP)
    # --------------------------------------------------

    def _leg_ramped(self, direction, speed, est_time):
        """
        One leg with multi-step ramp based on estimated time.
        """
        speed = min(abs(speed), 1.0)
        est_time = max(est_time, 0.2)

        self.train.throttle = direction * speed
        current_throttle = self.train.throttle

        t0 = time.monotonic()
        timeout = est_time * 3.0
        timeout = 10

        while True:
            now = time.monotonic()
            elapsed = now - t0
            progress = elapsed / est_time

            # Check for bumper hit
            if direction > 0 and self._right_hit():
                self.train.throttle = 0.0
                return elapsed
            if direction < 0 and self._left_hit():
                self.train.throttle = 0.0
                return elapsed

            if elapsed > timeout:
                self.train.throttle = 0.0
                raise RuntimeError("Timeout waiting for bumper in shuttle")

            # Apply multi-step ramp
            new_throttle = self._ramped_throttle(direction, speed, progress)
            if new_throttle != current_throttle:
                current_throttle = new_throttle
                self.train.throttle = new_throttle

            time.sleep(0.01)

    def _ramped_throttle(self, direction, base_speed, progress):
        """
        Multi-step ramp from base_speed down to *at least* min_throttle.
        Never goes below self.min_throttle.
        """
        base = max(abs(base_speed), self.min_throttle)

        # Clamp progress 0..1
        progress = max(0.0, min(1.0, progress))

        # Before ramp start: full base speed
        if progress < self.ramp_start_ratio:
            return direction * base

        # Compute where we are in the ramp segment
        if self.ramp_start_ratio >= 1.0:
            frac = 1.0
        else:
            frac = (progress - self.ramp_start_ratio) / (1.0 - self.ramp_start_ratio)
            frac = max(0.0, min(1.0, frac))

        # Step index 0..steps-1
        steps = max(1, self.ramp_steps)
        step_index = int(frac * steps)
        if step_index >= steps:
            step_index = steps - 1

        # Step level from 1/steps up to 1
        level = (step_index + 1) / steps

        # Linearly step from base -> min_throttle
        mag = base - (base - self.min_throttle) * level

        # Hard clamp: NEVER go below min_throttle
        if mag < self.min_throttle:
            mag = self.min_throttle

        return direction * mag
