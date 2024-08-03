def switch_state(l_sw, r_sw, upd_vol, h_down_sec):
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
