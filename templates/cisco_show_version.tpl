Value HOSTNAME (\S+)
Value SERIAL (\S+)

Start
  ^${HOSTNAME}\suptime.* -> Record
  ^Processor\sboard\sID\s${SERIAL} -> Record
