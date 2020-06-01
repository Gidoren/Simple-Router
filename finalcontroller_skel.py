# Final Skeleton
#
# Hints/Reminders from Lab 3:
#
# To check the source and destination of an IP packet, you can use
# the header information... For example:
#
# ip_header = packet.find('ipv4')
#
# if ip_header.srcip == "1.1.1.1":
#   print "Packet is from 1.1.1.1"
#
# Important Note: the "is" comparison DOES NOT work for IP address
# comparisons in this way. You must use ==.
# 
# To send an OpenFlow Message telling a switch to send packets out a
# port, do the following, replacing <PORT> with the port number the 
# switch should send the packets out:
#
  #  msg = of.ofp_flow_mod()
  #  msg.match = of.ofp_match.from_packet(packet)
  #  msg.idle_timeout = 30
  #  msg.hard_timeout = 30

  #  msg.actions.append(of.ofp_action_output(port = <PORT>))
  #  msg.data = packet_in
  #  self.connection.send(msg)

# To drop packets, simply omit the action.
#

from pox.core import core
import time
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class Final (object):
  """
  A Firewall object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

  def do_final (self, packet, packet_in, port_on_switch, switch_id,event):
    # This is where you'll put your code. The following modifications have 
    # been made from Lab 3:
    #   - port_on_switch: represents the port that the packet was received on.
    #   - switch_id represents the id of the switch that received the packet.
    #      (for example, s1 would have switch_id == 1, s2 would have switch_id == 2, etc...)
    # You should use these to determine where a packet came from. To figure out where a packet 
    # is going, you can use the IP header information.
    def portOut (portNum):
      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match.from_packet(packet)
      msg.idle_timeout = 30
      msg.hard_timeout = 30

      msg.actions.append(of.ofp_action_output(port = portNum))
      msg.data = packet_in
      self.connection.send(msg)


    def flood (message = None):
      """ Floods the packet """
      self.hold_down_expired = _flood_delay = 0
      msg = of.ofp_packet_out()
      if time.time() - self.connection.connect_time >= _flood_delay:
        # Only flood if we've been connected for a little while...

        if self.hold_down_expired is False:
          # Oh yes it is!
          self.hold_down_expired = True
          log.info("%s: Flood hold-down expired -- flooding",
              dpid_to_str(event.dpid))

        if message is not None: log.debug(message)
        #log.debug("%i: flood %s -> %s", event.dpid,packet.src,packet.dst)
        # OFPP_FLOOD is optional; on some switches you may need to change
        # this to OFPP_ALL.
        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
      else:
        pass
        #log.info("Holding down flood for %s", dpid_to_str(event.dpid))
      msg.data = event.ofp
      msg.in_port = event.port
      self.connection.send(msg)

    #gets the packet ipv4  
    ip_header = packet.find('ipv4')
    #checks if its an ip packet for routing rules
    if packet.type == packet.IP_TYPE:
      #gets the source ip of the host
      sourceIP = ip_header.srcip
      #gets the destination packet is being sent
      destIP = ip_header.dstip
      print sourceIP
      #if the host is the dangerous host
      if sourceIP == "123.45.67.89": 
        print "danger danger"
      #check if it isnt icmp include the ports of every switch port except to the switch before server
        noHost = packet.find("tcp")
        if noHost:
          if destIP != "10.5.5.50":
            if switch_id == 4:
              if destIP == "10.1.1.10":
                portOut(2)
              elif destIP == "10.2.2.20":
                portOut(3)
              elif destIP == "10.3.3.30":
                portOut(4)
            else:
              #if it isnt switch 4 send it through port 1
              portOut(1)
      else:
        #if we are on the central switch
        if switch_id == 4:
          if destIP == "10.1.1.10":
            portOut(2)
          elif destIP == "10.2.2.20":
            portOut(3)
          elif destIP == "10.3.3.30":
            portOut(4)
          elif destIP == "123.45.67.89":
            if sourceIP != "10.5.5.50":
              portOut(1)
          else:
            portOut(5)
            #if we are on the server switch
        elif switch_id == 5:
          if destIP == "10.5.5.50":
            portOut(1)
          else:
            portOut(2)
            #if we are on switches 1-3
        elif switch_id == 1:
          if destIP == "10.1.1.10":
            portOut(1)
          else:
            portOut(2)
        elif switch_id == 2:
          if destIP == "10.2.2.20":
            portOut(1)
          else:
            portOut(2)
        elif switch_id == 3:
          if destIP == "10.3.3.30":
            portOut(1)
          else:
            portOut(2)
    else:
      flood()

  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    self.do_final(packet, packet_in, event.port, event.dpid,event)

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Final(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
