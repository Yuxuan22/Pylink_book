# Filename: broadcast_simple.py

import pylink
listener = pylink.EyeLinkListener()

print('wait for the primary connection to the tracker')
link_connected = 0
while not link_connected:
    # access link status info, returns an instance of the ILinkData class
    idata = listener.getTrackerInfo()    
    listener.requestTime()# force tracker to send status and time
    t = pylink.currentTime()
    while(pylink.currentTime()-t < 500):   # wait for response 
        tt = listener.readTime()   # will be nonzero if reply 
        if tt is not 0: # extract connection state
            if (idata.getLinkFlags() & pylink.LINK_CONNECTED):
                print('Link Status: %s - connected' % idata.getLinkFlags())
                link_connected = pylink.LINK_CONNECTED
                break

# send over command to instruct the Host PC to enter the broadcasting mode
listener.broadcastOpen()

# in a while loop, check the current operation mode of the tracker
# and save the sample data (gaze position) to file if in recording mode
smp_data = open('sample_data.csv', 'w')
mode = -1
smp_t = -32768 # initial timestamp for samples
while listener.isConnected():
    current_mode = listener.getTrackerMode() # get the curent Host mode
    # print a warning message when switching modes
    if current_mode is not mode:
        mode = current_mode
        if current_mode == pylink.EL_SETUP_MENU_MODE:
            print('Current mode: %d - EL_SETUP_MENU_MODE' % mode)
        if current_mode == pylink.EL_CALIBRATE_MODE:
            print('Current mode: %d - EL_CALIBRATE_MODE' % mode)
        if current_mode == pylink.EL_OPTIONS_MENU_MODE:
            print('Current mode: %d - EL_OPTIONS_MENU_MODE' % mode)
        if current_mode == pylink.EL_VALIDATE_MODE:
            print('Current mode: %d - EL_VALIDATE_MODE' % mode)
        if current_mode == pylink.EL_DRIFT_CORR_MODE:
            print('Current mode: %d - EL_DRIFT_CORR_MODE' % mode)
        if current_mode == pylink.EL_RECORD_MODE:
            print('Current mode: %d - EL_RECORD_MODE' % mode)
    
    # retrieve sample data if were in RECORD_MODE
    if current_mode == pylink.EL_RECORD_MODE:
        smp = listener.getNewestSample()
        if (smp is not None) and (smp.getTime() != smp_t):
            smp_t = smp.getTime()
            if smp.isRightSample():
                gaze_x, gaze_y = smp.getRightEye().getGaze()
            elif smp.isLeftSample():
                gaze_x, gaze_y = smp.getLeftEye().getGaze()
            # write the gaze position to file
            smp_data.write('%d, %d, %d\n' %(smp_t, gaze_x, gaze_y))
