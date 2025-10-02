Value Required INTERFACE (\S+)
Value IP (\S+)
Value OK (YES|NO)
Value METHOD (manual|dhcp|unset)
Value STATUS (administratively down|up|down)
Value PROTOCOL (up|down)

Start
  ^${INTERFACE}\s+${IP}\s+${OK}\s+${METHOD}\s+${STATUS}\s+${PROTOCOL} -> Record
