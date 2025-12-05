import viz
import vizcam
import vizshape
import vizact
import random

# ---------- Setup ----------
viz.setOption('viz.fullscreen', '1')
viz.go()

# --------- walk and mouse ----------
vizcam.WalkNavigate(forward='w', backward='s', left='a', right='d', moveScale=2, turnScale=0.5)
viz.mouse.setVisible(False)
viz.mouse.setTrap(viz.ON)
viz.MainView.collision(True)

# --------- jumping ----------
isJumping = False
jumpHeight = 3.0
jumpDuration = 0.8
jumpStartY = 0
jumpStartTime = 0
jumpTimer = None

def jump():
    global isJumping, jumpStartTime, jumpStartY, jumpTimer
    if not isJumping:
        isJumping = True
        jumpStartTime = viz.tick()
        jumpStartY = viz.MainView.getPosition()[1]
        jumpTimer = vizact.ontimer(0, updateJump)

def updateJump():
    global isJumping, jumpStartTime, jumpStartY, jumpTimer
    if not isJumping:
        return
    elapsed = viz.tick() - jumpStartTime
    progress = elapsed / jumpDuration
    if progress >= 1.0:
        currentPos = viz.MainView.getPosition()
        viz.MainView.setPosition([currentPos[0], jumpStartY, currentPos[2]])
        isJumping = False
        if jumpTimer:
            jumpTimer.remove()
            jumpTimer = None
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

# --------- inventory system ----------
MAX_INVENTORY_SLOTS = 5
inventory = [None] * MAX_INVENTORY_SLOTS
inventoryUI = []
selectedSlot = 0

def createInventoryUI():
    global inventoryUI
    inventoryUI = []
    for i in range(MAX_INVENTORY_SLOTS):
        x_pos = 0.25 + (i * 0.13)
        slotBG = viz.addText('[     ]', parent=viz.SCREEN)
        slotBG.setPosition(x_pos, 0.1)
        slotBG.fontSize(42)
        slotBG.alignment(viz.ALIGN_CENTER_CENTER)
        slotBG.color(1,1,0 if i == selectedSlot else 0.7)
        slotText = viz.addText(str(i + 1), parent=viz.SCREEN)
        slotText.setPosition(x_pos, 0.05)
        slotText.fontSize(20)
        slotText.alignment(viz.ALIGN_CENTER_CENTER)
        codeText = viz.addText('', parent=viz.SCREEN)
        codeText.setPosition(x_pos, 0.105)
        codeText.fontSize(18)
        codeText.alignment(viz.ALIGN_CENTER_CENTER)
        codeText.color(1,1,0)
        codeText.visible(False)
        inventoryUI.append({
            'background': slotBG,
            'slotNumber': slotText,
            'codeText': codeText
        })

def updateInventoryUI():
    for i in range(MAX_INVENTORY_SLOTS):
        inventoryUI[i]['background'].color(
            1,1,0 if i == selectedSlot else 0.7
        )
        if inventory[i] and inventory[i]['type'] == 'code':
            codePart = inventory[i]['name'].split(': ')[1]
            inventoryUI[i]['codeText'].message(codePart)
            inventoryUI[i]['codeText'].visible(True)
        else:
            inventoryUI[i]['codeText'].visible(False)

def addToInventory(itemName, itemType='generic'):
    for i in range(MAX_INVENTORY_SLOTS):
        if inventory[i] is None:
            inventory[i] = {'name': itemName, 'type': itemType}
            updateInventoryUI()
            return True
    return False

def removeFromInventory(slotIndex):
    if inventory[slotIndex]:
        inventory[slotIndex] = None
        updateInventoryUI()
        return True
    return False

def useItem(slotIndex):
    if inventory[slotIndex]:
        if inventory[slotIndex]['type'] == 'code':
            print("Code cannot be used with E")
            return None
        removed = inventory[slotIndex]
        inventory[slotIndex] = None
        updateInventoryUI()
        return removed
    return None

def selectInventorySlot(slotNumber):
    global selectedSlot
    selectedSlot = slotNumber
    updateInventoryUI()

vizact.onkeydown('1', lambda: selectInventorySlot(0))
vizact.onkeydown('2', lambda: selectInventorySlot(1))
vizact.onkeydown('3', lambda: selectInventorySlot(2))
vizact.onkeydown('4', lambda: selectInventorySlot(3))
vizact.onkeydown('5', lambda: selectInventorySlot(4))
vizact.onkeydown('e', lambda: useItem(selectedSlot))
vizact.onkeydown('q', lambda: removeFromInventory(selectedSlot))

# --------- crosshair ----------
crosshair = viz.addText('+', parent=viz.SCREEN)
crosshair.setPosition(0.5,0.5)
crosshair.fontSize = 24
crosshair.alignment(viz.ALIGN_CENTER_CENTER)

# --------- STICKY NOTE ----------
noteCode = str(random.randint(1000, 9999))
noteObject = None
notePickedUp = False
NOTE_POSITION = [-7.2, 5.7, 11.2]
NOTE_PICKUP_RADIUS = 2.0

def createNote():
    global noteObject
    noteObject = viz.addChild('StickyNote.fbx')
    noteObject.setPosition(NOTE_POSITION)
    noteObject.setScale([0.5,0.5,0.5])
    noteObject.setEuler([0, 180, 0])
    noteObject.disable(viz.DYNAMICS)
    print("Sticky note created at:", noteObject.getPosition())

def checkNotePickup():
    if not noteObject or notePickedUp:
        return
    p = viz.MainView.getPosition()
    n = noteObject.getPosition()
    d = ((p[0]-n[0])**2 + (p[1]-n[1])**2 + (p[2]-n[2])**2) ** 0.5
    if d < NOTE_PICKUP_RADIUS:
        crosshair.color(1,1,0)
    else:
        crosshair.color(1,1,1)

# --------- SAFE SYSTEM ----------
SAFE_POSITION = [-5, 5.7, 9]
SAFE_RADIUS = 2.0
safeLocked = True
keyTaken = False
KEY_ITEM_NAME = "Door Key"

def checkSafeProximity():
    if safeLocked and not keyTaken:
        p = viz.MainView.getPosition()
        dist = ((p[0]-SAFE_POSITION[0])**2 + (p[1]-SAFE_POSITION[1])**2 + (p[2]-SAFE_POSITION[2])**2) ** 0.5
        if dist < SAFE_RADIUS:
            crosshair.color(0,1,1)  # cyan
        else:
            crosshair.color(1,1,1)

# --------- DOOR SYSTEM ----------
DOOR_POSITION = [-2, 0, 14]
DOOR_RADIUS = 2.5
doorLocked = True

def checkDoorProximity():
    p = viz.MainView.getPosition()
    dist = ((p[0]-DOOR_POSITION[0])**2 + (p[1]-DOOR_POSITION[1])**2 + (p[2]-DOOR_POSITION[2])**2) ** 0.5
    if dist < DOOR_RADIUS:
        crosshair.color(0,1,0)
    else:
        crosshair.color(1,1,1)

# --------- F key: note pickup & safe unlock ----------
def onKeyF():
    global notePickedUp, noteObject, safeLocked, keyTaken
    p = viz.MainView.getPosition()

    # Try pickup note
    if noteObject and not notePickedUp:
        n = noteObject.getPosition()
        d_note = ((p[0]-n[0])**2 + (p[1]-n[1])**2 + (p[2]-n[2])**2) ** 0.5
        if d_note < NOTE_PICKUP_RADIUS:
            addToInventory(f"Safe Code: {noteCode}", "code")
            noteObject.remove()
            noteObject = None
            notePickedUp = True
            print("Sticky note picked up! Code:", noteCode)
            return

    # Try unlock safe
    if safeLocked and not keyTaken:
        dist_safe = ((p[0]-SAFE_POSITION[0])**2 + (p[1]-SAFE_POSITION[1])**2 + (p[2]-SAFE_POSITION[2])**2) ** 0.5
        if dist_safe < SAFE_RADIUS:
            hasCode = any(item and item['type'] == 'code' for item in inventory)
            if hasCode:
                print("Correct code! Safe unlocked.")
                safeLocked = False
                addToInventory(KEY_ITEM_NAME, "key")
                keyTaken = True
            else:
                print("The safe is locked. You need the code.")

vizact.onkeydown('f', onKeyF)

# --------- T key: open door ----------
def tryOpenDoor():
    global doorLocked
    p = viz.MainView.getPosition()
    dist = ((p[0]-DOOR_POSITION[0])**2 + (p[1]-DOOR_POSITION[1])**2 + (p[2]-DOOR_POSITION[2])**2) ** 0.5
    if dist > DOOR_RADIUS:
        return
    if doorLocked:
        hasKey = any(item and item['name'] == KEY_ITEM_NAME for item in inventory)
        if hasKey:
            print("Door unlocked! You escaped!")
            doorLocked = False
            viz.quit()
        else:
            print("The door is locked. You need a key.")

vizact.onkeydown('t', tryOpenDoor)

# ---------- OPEN SAFE -----------------
safeDoor = room.getTransform('safeDoor')

def openSafeAnim():
    action = vizact.spin(0, -180, 0, speed=20, dur=2.0)
    safeDoor.addAction(action)

vizact.onkeydown('g', openSafeAnim)

# --------- INIT ----------
def initializeInventoryUI():
    createInventoryUI()
    createNote()
    vizact.ontimer2(0,0.1,checkNotePickup)
    vizact.ontimer2(0,0.1,checkSafeProximity)
    vizact.ontimer2(0,0.1,checkDoorProximity)

vizact.ontimer(0.5, initializeInventoryUI)
