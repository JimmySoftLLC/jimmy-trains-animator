def switch_state_trigger(l_sw, r_sw, t_sw, upd_vol, h_down_sec, override_switch_state = None):
    if override_switch_state and override_switch_state["switch_value"]:
        return_parameter = override_switch_state["switch_value"]
        override_switch_state["switch_value"] = ""
        return return_parameter
    l_sw.update()
    r_sw.update()
    t_sw.update()
    if l_sw.fell: 
        chk = True
        cyc = 0  
        while chk:
            upd_vol(.1)
            l_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "left_held" 
            if l_sw.rose:
                print ("left pressed")
                return "left" 
    if r_sw.fell:
        chk = True
        cyc = 0  
        while chk:
            upd_vol(.1)
            r_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "right_held" 
            if r_sw.rose:
                print ("right pressed")
                return "right"
    if t_sw.fell: 
        chk = True
        cyc = 0  
        while chk:
            upd_vol(.1)
            t_sw.update()
            if t_sw.rose:
                print ("trigger pressed")
                return "trigger" 
    if not l_sw.value:
        chk = True
        cyc = 0  
        while chk:
            upd_vol(.1)
            l_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "left_held" 
            if l_sw.rose:
                return "none"
    if not r_sw.value:
        chk = True
        cyc = 0  
        while chk:
            upd_vol(.1)
            r_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "right_held" 
            if r_sw.rose:
                return "none"
    upd_vol(0.1)
    return "none"

def switch_state(l_sw, r_sw, upd_vol, h_down_sec, override_switch_state=None, wait_at_end = True):
    if override_switch_state and override_switch_state["switch_value"]:
        return_parameter = override_switch_state["switch_value"]
        override_switch_state["switch_value"] = ""
        return return_parameter
    l_sw.update()
    r_sw.update()
    if l_sw.fell:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            l_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "left_held"
            if l_sw.rose:
                return "left"
    if r_sw.fell:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            r_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "right_held"
            if r_sw.rose:
                return "right"
    if not l_sw.value:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            l_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "left_held"
            if l_sw.rose:
                return "none"
    if not r_sw.value:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            r_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "right_held"
            if r_sw.rose:
                return "none"
    if wait_at_end:
        upd_vol(0.1)
    return "none"


def switch_state_four_switches(l_sw, r_sw, three_sw, four_sw, upd_vol, h_down_sec, override_switch_state=None, wait_at_end = True):
    if override_switch_state and override_switch_state["switch_value"]:
        return_parameter = override_switch_state["switch_value"]
        override_switch_state["switch_value"] = ""
        return return_parameter
    l_sw.update()
    r_sw.update()
    three_sw.update()
    four_sw.update()
    if l_sw.fell:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            l_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "left_held"
            if l_sw.rose:
                return "left"
    if r_sw.fell:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            r_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "right_held"
            if r_sw.rose:
                return "right"
    if three_sw.fell:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            three_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "three_held"
            if three_sw.rose:
                return "three"
    if four_sw.fell:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            four_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "four_held"
            if four_sw.rose:
                return "four"
    if not l_sw.value:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            l_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "left_held"
            if l_sw.rose:
                return "none"
    if not r_sw.value:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            r_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "right_held"
            if r_sw.rose:
                return "none"
    if not three_sw.value:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            three_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "three_held"
            if three_sw.rose:
                return "none"
    if not four_sw.value:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            four_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "four_held"
            if four_sw.rose:
                return "none"
    if wait_at_end:
        upd_vol(0.1)
    return "none"


def switch_state_five_switches(l_sw, r_sw, three_sw, four_sw, five_sw, upd_vol, h_down_sec, override_switch_state=None, wait_at_end = True):
    if override_switch_state and override_switch_state["switch_value"]:
        return_parameter = override_switch_state["switch_value"]
        override_switch_state["switch_value"] = ""
        return return_parameter
    l_sw.update()
    r_sw.update()
    three_sw.update()
    four_sw.update()
    five_sw.update()
    if l_sw.fell:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            l_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "left_held"
            if l_sw.rose:
                return "left"
    if r_sw.fell:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            r_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "right_held"
            if r_sw.rose:
                return "right"
    if three_sw.fell:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            three_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "three_held"
            if three_sw.rose:
                return "three"
    if four_sw.fell:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            four_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "four_held"
            if four_sw.rose:
                return "four"
    if five_sw.fell:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            five_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "five_held"
            if five_sw.rose:
                return "five"
    if not l_sw.value:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            l_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "left_held"
            if l_sw.rose:
                return "none"
    if not r_sw.value:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            r_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "right_held"
            if r_sw.rose:
                return "none"
    if not three_sw.value:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            three_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "three_held"
            if three_sw.rose:
                return "none"
    if not four_sw.value:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            four_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "four_held"
            if four_sw.rose:
                return "none"
    if not five_sw.value:
        chk = True
        cyc = 0
        while chk:
            upd_vol(.1)
            five_sw.update()
            cyc += 1
            if cyc > h_down_sec*10:
                return "five_held"
            if five_sw.rose:
                return "none"
    if wait_at_end:
        upd_vol(0.1)
    return "none"


def switch_state_trolley(l_sw, r_sw, upd_vol, h_down_sec, override_switch_state=None, wait_at_end=True):
    if override_switch_state and override_switch_state["switch_value"]:
        return_parameter = override_switch_state["switch_value"]
        override_switch_state["switch_value"] = ""
        return return_parameter

    l_sw.update()
    r_sw.update()

    # --------------------------------------------------
    # LEFT PRESSED FIRST
    # --------------------------------------------------

    if l_sw.fell:
        cyc = 0

        while True:
            upd_vol(.1)

            l_sw.update()
            r_sw.update()

            # RIGHT was pressed while LEFT is down.
            if r_sw.fell:
                both_cyc = 0

                while True:
                    upd_vol(.1)

                    l_sw.update()
                    r_sw.update()

                    both_cyc += 1

                    if both_cyc > h_down_sec * 10:
                        return "both_held"

                    if l_sw.rose or r_sw.rose:
                        print("both pressed")
                        return "both"

            cyc += 1

            if cyc > h_down_sec * 10:
                return "left_held"

            if l_sw.rose:
                print("left pressed")
                return "left"

    # --------------------------------------------------
    # RIGHT PRESSED FIRST
    # --------------------------------------------------

    if r_sw.fell:
        cyc = 0

        while True:
            upd_vol(.1)

            l_sw.update()
            r_sw.update()

            # LEFT was pressed while RIGHT is down.
            if l_sw.fell:
                both_cyc = 0

                while True:
                    upd_vol(.1)

                    l_sw.update()
                    r_sw.update()

                    both_cyc += 1

                    if both_cyc > h_down_sec * 10:
                        return "both_held"

                    if l_sw.rose or r_sw.rose:
                        print("both pressed")
                        return "both"

            cyc += 1

            if cyc > h_down_sec * 10:
                return "right_held"

            if r_sw.rose:
                print("right pressed")
                return "right"

    # --------------------------------------------------
    # LEFT WAS ALREADY DOWN
    #
    # Same recovery logic as your existing switch_state().
    # --------------------------------------------------

    if not l_sw.value:
        cyc = 0

        while True:
            upd_vol(.1)

            l_sw.update()
            r_sw.update()

            if r_sw.fell:
                both_cyc = 0

                while True:
                    upd_vol(.1)

                    l_sw.update()
                    r_sw.update()

                    both_cyc += 1

                    if both_cyc > h_down_sec * 10:
                        return "both_held"

                    if l_sw.rose or r_sw.rose:
                        return "both"

            cyc += 1

            if cyc > h_down_sec * 10:
                return "left_held"

            if l_sw.rose:
                return "none"

    # --------------------------------------------------
    # RIGHT WAS ALREADY DOWN
    # --------------------------------------------------

    if not r_sw.value:
        cyc = 0

        while True:
            upd_vol(.1)

            l_sw.update()
            r_sw.update()

            if l_sw.fell:
                both_cyc = 0

                while True:
                    upd_vol(.1)

                    l_sw.update()
                    r_sw.update()

                    both_cyc += 1

                    if both_cyc > h_down_sec * 10:
                        return "both_held"

                    if l_sw.rose or r_sw.rose:
                        return "both"

            cyc += 1

            if cyc > h_down_sec * 10:
                return "right_held"

            if r_sw.rose:
                return "none"

    if wait_at_end:
        upd_vol(.1)

    return "none"