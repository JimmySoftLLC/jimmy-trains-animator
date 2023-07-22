def switch_state(left_switch, right_switch, sleepAndUpdateVolume, time_to_check):
    left_switch.update()
    right_switch.update()
    if left_switch.fell: 
        button_check = True
        number_cycles = 0  
        while button_check:
            sleepAndUpdateVolume(.01)
            left_switch.update()
            number_cycles += 1
            if number_cycles > time_to_check*100:
                print ("left held")
                return "left_held" 
            if left_switch.rose:
                print ("left pressed")
                return "left" 
    if right_switch.fell:
        button_check = True
        number_cycles = 0  
        while button_check:
            sleepAndUpdateVolume(.01)
            right_switch.update()
            number_cycles += 1
            if number_cycles > time_to_check*100:
                print ("right held")
                return "right_held" 
            if right_switch.rose:
                print ("right pressed")
                return "right"
    if not left_switch.value:
        button_check = True
        number_cycles = 0  
        while button_check:
            sleepAndUpdateVolume(.01)
            left_switch.update()
            number_cycles += 1
            if number_cycles > time_to_check*100:
                print ("left held")
                return "left_held" 
            if left_switch.rose:
                print ("none")
                return "none"
    if not right_switch.value:
        button_check = True
        number_cycles = 0  
        while button_check:
            sleepAndUpdateVolume(.01)
            right_switch.update()
            number_cycles += 1
            if number_cycles > time_to_check*100:
                print ("right held")
                return "right_held" 
            if right_switch.rose:
                print ("none")
                return "none"
    return "none"
