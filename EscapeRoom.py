import viz
import vizcam
import vizshape
import vizact
import random
import math

# ---------- setup ----------
viz.setOption('viz.fullscreen', '1')
viz.go()

# --------- walk and mouse ----------
vizcam.WalkNavigate(forward='w', backward='s', left='a', right='d', moveScale=2, turnScale=0.5)
viz.mouse.setVisible(False)
viz.mouse.setTrap(viz.ON)
viz.MainView.collision(True)

#---------- MODEL ------------------

room = viz.addChild('TestRoom.osgb')
room.setPosition(-10, 0, -10)
room.setScale([0.05, 0.05, 0.05])
room.enable(viz.LIGHTING)

movingBooks = room.getTransform('movingBooks') 

def kustinatGramatu():
    # piemērs: pārvieto gleznas mezglu malā pa x asi
    # vizact.movelocal var būt noderīgs, bet vienkārši var izmantot vizact.moveTo
	action = vizact.moveTo([339.81381, 120, 92.62527], time=2.0, interpolate=vizact.easeInOut)
	movingBook = movingBooks
	movingBook.addAction(action)

# saista funkciju ar pogu (piemēram, “g” taustiņu)
vizact.onkeydown('g', kustinatGramatu)