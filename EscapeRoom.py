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

# --------- jumping ----------
#
isJumping = False
jumpHeight = 3.0
jumpDuration = 0.8
jumpStartY = 0
jumpStartTime = 0

def jump():
    global isJumping, jumpStartTime, jumpStartY
    if not isJumping:
        isJumping = True
        jumpStartTime = viz.tick()
        jumpStartY = viz.MainView.getPosition()[1]
        vizact.ontimer(0, updateJump)

def updateJump():
    global isJumping, jumpStartTime, jumpStartY
    if not isJumping:
        return
    
    elapsed = viz.tick() - jumpStartTime
    progress = elapsed / jumpDuration
    
    if progress >= 1.0:
        currentPos = viz.MainView.getPosition()
        viz.MainView.setPosition([currentPos[0], jumpStartY, currentPos[2]])
        isJumping = False
        vizact.killtimer(updateJump)
        return
    
    if progress <= 0.5:
        t = progress * 2
        height = jumpStartY + jumpHeight * (1 - (1 - t) ** 2)
    else:
        t = (progress - 0.5) * 2
        height = jumpStartY + jumpHeight * (1 - t ** 2)
    
    currentPos = viz.MainView.getPosition()
    viz.MainView.setPosition([currentPos[0], height, currentPos[2]])

vizact.onkeydown(' ', jump)

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