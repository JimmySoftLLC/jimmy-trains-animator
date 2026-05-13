# safemode.py
import alarm
import microcontroller
import supervisor
import time

#if supervisor.runtime.safe_mode_reason == supervisor.SafeModeReason.BROWNOUT:
    # Sleep for ten minutes and then run code.py again.
#    time_alarm = alarm.time.TimeAlarm(monotonic_time = time.monotonic + 10)
#    alarm.exit_and_deep_sleep_until_alarms(time_alarm)

time.sleep(8)

microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
microcontroller.reset()

