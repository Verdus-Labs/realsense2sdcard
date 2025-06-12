## HOW TO RUN
##### server-side
1. Get your computer's IP
2. Run `python3 udp_rgbd_receiver.py` at root

##### rpi-side
1. Enter the python env "rsvenv" by running `source rsvenv/bin/activate`
2. Run `python3 udp_rgbd_streamer.py insert_computer_ip`
   
the RGB and Depth viewers should pop up on your computer with a successful UDP connection