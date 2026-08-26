import time


class TrolleyController:
    """
    Simple trolley controller.

    Assumptions:
      - train.throttle is in [-1.0 .. 1.0]
      - l_sw_io.value == True when LEFT bumper is hit
      - r_sw_io.value == True when RIGHT bumper is hit
    """

    def __init__(self, train, l_sw_io, r_sw_io, ramp_start_ratio=0.7, min_throttle=0.08, off_bumper_time=0.3, ramp_steps=3):
        self.train = train
        self.l_sw_io = l_sw_io
        self.r_sw_io = r_sw_io

        self.ramp_start_ratio = float(ramp_start_ratio)
        self.min_throttle = float(min_throttle)
        self.off_bumper_time = float(off_bumper_time)
        self.ramp_steps = int(ramp_steps)

        self.base_speed = None
        self.time_forward = None
        self.time_reverse = None

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------

    def calibrate(self, speed=0.3, cycles=3):
        """
        Calibrate travel time between bumpers at a fixed speed.

        Returns True if calibration succeeds.
        Returns False if calibration fails.

        No exceptions are raised for normal trolley problems.
        """

        s = abs(float(speed))

        if s <= 0:
            print("Trolley calibration error: speed must be greater than 0")
            self.train.throttle = 0.0
            return False

        if s > 1.0:
            s = 1.0

        if cycles < 1:
            cycles = 1

        self.base_speed = s

        f_times = []
        r_times = []

        for cycle in range(cycles):
            print("Calibration cycle:", cycle + 1)

            # --------------------------------------------------
            # LEFT -> RIGHT
            # --------------------------------------------------

            t_f = self._leg_constant(+1, s)

            if t_f is None:
                print("Calibration failed going toward right bumper")
                self.train.throttle = 0.0
                return False

            f_times.append(t_f)

            self._back_off(+1)

            # --------------------------------------------------
            # RIGHT -> LEFT
            # --------------------------------------------------

            t_r = self._leg_constant(-1, s)

            if t_r is None:
                print("Calibration failed going toward left bumper")
                self.train.throttle = 0.0
                return False

            r_times.append(t_r)

            self._back_off(-1)

        if len(f_times) == 0 or len(r_times) == 0:
            print("Trolley calibration failed: no valid travel times")
            self.train.throttle = 0.0
            return False

        self.time_forward = sum(f_times) / len(f_times)
        self.time_reverse = sum(r_times) / len(r_times)

        print("Trolley calibration complete")
        print("Forward time:", self.time_forward)
        print("Reverse time:", self.time_reverse)

        return True

    def shuttle(self, start_direction, cycles=None):
        """
        Run back and forth between bumpers.

        start_direction:
            +1 = move toward RIGHT bumper
            -1 = move toward LEFT bumper

        cycles:
            Number of one-way trips.
            None = continue indefinitely.

        Returns True if completed normally.
        Returns False if a problem occurs.
        """

        if start_direction > 0:
            direction = +1

        elif start_direction < 0:
            direction = -1

        else:
            print("Trolley error: start_direction must be +1 or -1")
            self.train.throttle = 0.0
            return False

        if self.base_speed is None:
            print("Trolley error: trolley has not been calibrated")
            self.train.throttle = 0.0
            return False

        if self.time_forward is None:
            print("Trolley error: forward travel time is not available")
            self.train.throttle = 0.0
            return False

        if self.time_reverse is None:
            print("Trolley error: reverse travel time is not available")
            self.train.throttle = 0.0
            return False

        min_est = 0.2

        t_f = max(self.time_forward, min_est)
        t_r = max(self.time_reverse, min_est)

        count = 0

        while True:
            if direction > 0:
                est = t_f
            else:
                est = t_r

            est = max(est, min_est)

            actual = self._leg_ramped(direction, self.base_speed, est)

            if actual is None:
                print("Trolley shuttle stopped because bumper was not reached")
                self.train.throttle = 0.0
                return False

            if direction > 0:
                t_f = 0.9 * t_f + 0.1 * actual
            else:
                t_r = 0.9 * t_r + 0.1 * actual

            self._back_off(direction)

            direction *= -1
            count += 1

            if cycles is not None and count >= cycles:
                break

        self.train.throttle = 0.0

        self.time_forward = t_f
        self.time_reverse = t_r

        return True

    # --------------------------------------------------
    # SWITCH HELPERS
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
        Move away from bumper for a fixed amount of time.

        Switches are intentionally ignored while backing off.
        """

        if mag is None:
            if self.base_speed is not None:
                mag = self.base_speed
            else:
                mag = 0.3

        mag = min(abs(mag), 1.0)

        self.train.throttle = -direction * mag

        t0 = time.monotonic()

        while time.monotonic() - t0 < self.off_bumper_time:
            time.sleep(0.01)

        self.train.throttle = 0.0

    # --------------------------------------------------
    # CALIBRATION LEG
    # --------------------------------------------------

    def _leg_constant(self, direction, speed):
        """
        Run at constant speed until target bumper is reached.

        Returns elapsed travel time on success.
        Returns None on timeout.
        """

        speed = min(abs(speed), 1.0)

        self.train.throttle = direction * speed

        t0 = time.monotonic()
        timeout = 60.0

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

                if direction > 0:
                    print("Calibration timeout waiting for RIGHT bumper")
                else:
                    print("Calibration timeout waiting for LEFT bumper")

                return None

            time.sleep(0.01)

    # --------------------------------------------------
    # SHUTTLE LEG
    # --------------------------------------------------

    def _leg_ramped(self, direction, speed, est_time):
        """
        Run one shuttle leg using the estimated travel time
        to slow the trolley as it approaches the bumper.

        Returns elapsed travel time on success.
        Returns None on timeout.
        """

        speed = min(abs(speed), 1.0)
        est_time = max(est_time, 0.2)

        self.train.throttle = direction * speed
        current_throttle = self.train.throttle

        t0 = time.monotonic()

        timeout = est_time * 3.0

        if timeout < 10.0:
            timeout = 10.0

        while True:
            now = time.monotonic()
            elapsed = now - t0

            progress = elapsed / est_time

            # --------------------------------------------------
            # BUMPER CHECK
            # --------------------------------------------------

            if direction > 0 and self._right_hit():
                self.train.throttle = 0.0
                return elapsed

            if direction < 0 and self._left_hit():
                self.train.throttle = 0.0
                return elapsed

            # --------------------------------------------------
            # SAFETY TIMEOUT
            # --------------------------------------------------

            if elapsed > timeout:
                self.train.throttle = 0.0

                if direction > 0:
                    print("Trolley timeout waiting for RIGHT bumper")
                else:
                    print("Trolley timeout waiting for LEFT bumper")

                return None

            # --------------------------------------------------
            # RAMP
            # --------------------------------------------------

            new_throttle = self._ramped_throttle(direction, speed, progress)

            if new_throttle != current_throttle:
                current_throttle = new_throttle
                self.train.throttle = new_throttle

            time.sleep(0.01)

    def _ramped_throttle(self, direction, base_speed, progress):
        """
        Multi-step slowdown from base speed to min_throttle.
        """

        base = max(abs(base_speed), self.min_throttle)

        progress = max(0.0, min(1.0, progress))

        if progress < self.ramp_start_ratio:
            return direction * base

        if self.ramp_start_ratio >= 1.0:
            frac = 1.0
        else:
            frac = (progress - self.ramp_start_ratio) / (1.0 - self.ramp_start_ratio)
            frac = max(0.0, min(1.0, frac))

        steps = max(1, self.ramp_steps)

        step_index = int(frac * steps)

        if step_index >= steps:
            step_index = steps - 1

        level = (step_index + 1) / steps

        mag = base - (base - self.min_throttle) * level

        if mag < self.min_throttle:
            mag = self.min_throttle

        return direction * mag