def switch_state(left_switch, right_switch, sleepAndUpdateVolume, held_down_seconds):
    left_switch.update()
    right_switch.update()
    if left_switch.fell: 
        button_check = True
        number_cycles = 0  
        while button_check:
            sleepAndUpdateVolume(.1)
            left_switch.update()
            number_cycles += 1
            if number_cycles > held_down_seconds*10:
                return "left_held" 
            if left_switch.rose:
                print ("left pressed")
                return "left" 
    if right_switch.fell:
        button_check = True
        number_cycles = 0  
        while button_check:
            sleepAndUpdateVolume(.1)
            right_switch.update()
            number_cycles += 1
            if number_cycles > held_down_seconds*10:
                return "right_held" 
            if right_switch.rose:
                print ("right pressed")
                return "right"
    if not left_switch.value:
        button_check = True
        number_cycles = 0  
        while button_check:
            sleepAndUpdateVolume(.1)
            left_switch.update()
            number_cycles += 1
            if number_cycles > held_down_seconds*10:
                return "left_held" 
            if left_switch.rose:
                return "none"
    if not right_switch.value:
        button_check = True
        number_cycles = 0  
        while button_check:
            sleepAndUpdateVolume(.1)
            right_switch.update()
            number_cycles += 1
            if number_cycles > held_down_seconds*10:
                return "right_held" 
            if right_switch.rose:
                return "none"
    sleepAndUpdateVolume(0.1)
    return "none"