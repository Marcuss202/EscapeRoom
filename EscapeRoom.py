import viz
import vizcam
import vizshape
import vizact
import random
import vizinfo

# ---------- Setup ----------
viz.setOption('viz.fullscreen', '0')
viz.go()

# ---------- MODEL ----------
room = viz.addChild('OldRoom.osgb')
if not room:
    print("ERROR: Failed to load room model")
else:
    print("Room model loaded successfully")
room.setPosition(10,0,0)
room.setScale([0.015,0.015,0.015])
room.enable(viz.LIGHTING)

# --------- background music ----------
bgMusic = viz.addAudio('../IntenseActionBgMusic.mp3')
bgMusic.volume(0.005)  # Quiet volume
bgMusic.loop(viz.LOOP)
bgMusic.play()

# --------- walk and mouse ----------
navigator = vizcam.WalkNavigate(forward='w', backward='s', left='a', right='d', moveScale=2, turnScale=0.5)
viz.mouse.setVisible(False)
viz.mouse.setTrap(viz.ON)
viz.MainView.collision(True)

# --------- jumping ----------
# isJumping = False
# jumpHeight = 3.0
# jumpDuration = 0.8
# jumpStartY = 0
# jumpStartTime = 0
# jumpTimer = None

# def jump():
#     global isJumping, jumpStartTime, jumpStartY, jumpTimer
#     if not isJumping:
#         isJumping = True
#         jumpStartTime = viz.tick()
#         jumpStartY = viz.MainView.getPosition()[1]
#         jumpTimer = vizact.ontimer(0, updateJump)

# def updateJump():
#     global isJumping, jumpStartTime, jumpStartY, jumpTimer
#     if not isJumping:
#         return
#     elapsed = viz.tick() - jumpStartTime
#     progress = elapsed / jumpDuration
#     if progress >= 1.0:
#         currentPos = viz.MainView.getPosition()
#         viz.MainView.setPosition([currentPos[0], jumpStartY, currentPos[2]])
#         isJumping = False
#         if jumpTimer:
#             jumpTimer.remove()
#             jumpTimer = None
#         return
#     if progress <= 0.5:
#         t = progress * 2
#         height = jumpStartY + jumpHeight * (1 - (1 - t) ** 2)
#     else:
#         t = (progress - 0.5) * 2
#         height = jumpStartY + jumpHeight * (1 - t ** 2)
#     currentPos = viz.MainView.getPosition()
#     viz.MainView.setPosition([currentPos[0], height, currentPos[2]])

# vizact.onkeydown(' ', jump)

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
        slotBG.fontSize = 42
        slotBG.alignment(viz.ALIGN_CENTER_CENTER)
        slotBG.color(1,1,0 if i == selectedSlot else 0.7)
        slotText = viz.addText(str(i+1), parent=viz.SCREEN)
        slotText.setPosition(x_pos,0.05)
        slotText.fontSize = 20
        slotText.alignment(viz.ALIGN_CENTER_CENTER)
        codeText = viz.addText('', parent=viz.SCREEN)
        codeText.setPosition(x_pos,0.105)
        codeText.fontSize = 18
        codeText.alignment(viz.ALIGN_CENTER_CENTER)
        codeText.color(1,1,0)
        codeText.visible = False
        inventoryUI.append({'background': slotBG,'slotNumber':slotText,'codeText':codeText})

def updateInventoryUI():
    for i in range(MAX_INVENTORY_SLOTS):
        inventoryUI[i]['background'].color(1,1,0 if i==selectedSlot else 0.7)
        if inventory[i] and inventory[i]['type']=='code':
            codePart = inventory[i]['name'].split(': ')[1]
            inventoryUI[i]['codeText'].message(codePart)
            inventoryUI[i]['codeText'].visible=True
        else:
            inventoryUI[i]['codeText'].visible=False

def addToInventory(itemName,itemType='generic'):
    for i in range(MAX_INVENTORY_SLOTS):
        if inventory[i] is None:
            inventory[i] = {'name':itemName,'type':itemType}
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
        if inventory[slotIndex]['type']=='code':
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
# noteObject = None
notePickedUp = False
# NOTE_PICKUP_RADIUS = 2.0

# def createNote():
#     global noteObject
#     noteObject = viz.addChild('StickyNote.fbx')
#     noteObject.disable(viz.DYNAMICS)
#     print("Sticky note created at:", noteObject.getPosition())

# def checkNotePickup():
#     if not noteObject or notePickedUp:
#         return
#     p = viz.MainView.getPosition()
#     n = noteObject.getPosition()
#     d = ((p[0]-n[0])**2 + (p[1]-n[1])**2 + (p[2]-n[2])**2) ** 0.5
#     if d < NOTE_PICKUP_RADIUS:
#         crosshair.color(1,1,0)
#     else:
#         crosshair.color(1,1,1)

# --------- DOOR SYSTEM ----------
DOOR_POSITION = [-2,0,14]
DOOR_RADIUS = 2.5
doorLocked = True

def checkDoorProximity():
    p = viz.MainView.getPosition()
    dist = ((p[0]-DOOR_POSITION[0])**2 + (p[1]-DOOR_POSITION[1])**2 + (p[2]-DOOR_POSITION[2])**2)**0.5
    if dist<DOOR_RADIUS:
        crosshair.color(0,1,0)
    else:
        crosshair.color(1,1,1)

def tryOpenDoor():
    global doorLocked
    p = viz.MainView.getPosition()
    dist = ((p[0]-DOOR_POSITION[0])**2 + (p[1]-DOOR_POSITION[1])**2 + (p[2]-DOOR_POSITION[2])**2)**0.5
    if dist>DOOR_RADIUS:
        return
    if doorLocked:
        hasKey = any(item and item['name']==KEY_ITEM_NAME for item in inventory)
        if hasKey:
            print("Door unlocked! You escaped!")
            doorLocked = False
            viz.quit()
        else:
            print("The door is locked. You need a key.")

vizact.onkeydown('t', tryOpenDoor)

# ------------ GUIs -------------------

safePanel = None
safeTextboxes = []
enterCallback = None
keypadCallback = None
autoFocusTimer = None

def safeGUI():
    # Disable movement - remove the navigator completely
    global navigator, safePanel, safeTextboxes, enterCallback, keypadCallback, autoFocusTimer
    try:
        navigator.remove()
    except Exception:
        pass
    navigator = None
    
    # Show mouse and release trap so player can't look/turn until Enter
    viz.mouse.setVisible(viz.ON)
    viz.mouse.setTrap(viz.OFF)
    viz.mouse.setOverride(viz.ON)
    
    # Create textbox for code entry
    codeTextbox = viz.addTextbox()
    codeTextbox.setLength(0.5)
    codeTextbox.setPosition(.5, .5)
    codeTextbox.fontSize(48)  # Make it bigger
    codeTextbox.setFocus(True)  # Automatically focus the textbox
    safeTextboxes = [codeTextbox]

    # Auto-defocus when 4 digits are entered
    def autoDefocus():
        global autoFocusTimer
        if not safeTextboxes:
            return
        text = safeTextboxes[0].get()
        if len(text) >= 4:
            safeTextboxes[0].setFocus(False)
            if autoFocusTimer:
                autoFocusTimer.remove()
                autoFocusTimer = None

    autoFocusTimer = vizact.ontimer(0, autoDefocus)
    
    # Add Enter key handlers to check code (both main Enter and keypad Enter)
    def onEnter():
        print("Enter key pressed!")
        checkSafeCode()
    
    # Register both return and keypad enter for reliability
    enterCallback = vizact.onkeydown(viz.KEY_RETURN, onEnter)
    keypadCallback = vizact.onkeydown(viz.KEY_KP_ENTER, onEnter)
    print("Safe GUI opened, Enter callbacks registered")
    
    return safeTextboxes

def closeSafeGUI():
    # Remove textbox
    global navigator, safePanel, safeTextboxes, enterCallback, keypadCallback, autoFocusTimer
    if safeTextboxes:
        for tb in safeTextboxes:
            tb.remove()
    safeTextboxes = []
    
    # Remove enter key callbacks
    if enterCallback:
        enterCallback.remove()
        enterCallback = None
    if keypadCallback:
        keypadCallback.remove()
        keypadCallback = None
    if autoFocusTimer:
        autoFocusTimer.remove()
        autoFocusTimer = None
    
    # Re-enable movement - recreate navigator
    navigator = vizcam.WalkNavigate(forward='w', backward='s', left='a', right='d', moveScale=2, turnScale=0.5)
    
    # Hide mouse and trap again
    viz.mouse.setVisible(viz.OFF)
    viz.mouse.setTrap(viz.ON)
    viz.mouse.setOverride(viz.OFF)

def checkSafeCode():
    global safeTextboxes, noteCode
    if not safeTextboxes:
        print("No textboxes!")
        return
    
    code = safeTextboxes[0].get()
    print(f"Checking code: '{code}' against '{noteCode}'")
    
    if code == noteCode:
        print("Correct code!")
        openSafeAnim()
        closeSafeGUI()
    else:
        print(f"Wrong code! You entered: {code}, correct is: {noteCode}")
        # Close GUI anyway so user can try again
        closeSafeGUI()

# ---------- OPEN SAFE -----------------

# These will be initialized after the model loads
safeDoor = None
safeDoorBox = None
noteObject = None
transformsInitialized = False

def initializeSafeTransforms():
    global safeDoor, safeDoorBox, noteObject, transformsInitialized
    if transformsInitialized:
        return
    
    print("Initializing safe transforms...")
    
    # Try to get each transform, but suppress errors if they don't exist
    viz.setOption('viz.linkable', False)
    try:
        safeDoor = room.getTransform('safeDoor')
    except:
        print("  safeDoor not found - that's OK")
    
    try:
        safeDoorBox = room.getTransform('safeDoorBox')
    except:
        print("  safeDoorBox not found - that's OK")
    
    try:
        noteObject = room.getTransform('stickyNote')
    except:
        print("  stickyNote not found - that's OK")
    
    viz.setOption('viz.linkable', True)
    transformsInitialized = True
    print("Safe transforms initialization complete")

def openSafeAnim():
    if safeDoor:
        action = vizact.spin(0, -180, 0, speed=20, dur=4.0)
        safeDoor.addAction(action)
    else:
        print("WARNING: Cannot open safe - safeDoor transform not available")

# ---------- INTERACTION HANDLERS ----------

def onClickPainting():
    paintingMoved = False

    painting = room.getTransform('painting')

    if painting and not paintingMoved:
        paintingMoved = True
        action = vizact.moveTo([ -10.80915, 36.40491, -97.85873], time=0.5)
        painting.addAction(action)
    else:
        print("WARNING: Cannot move painting - painting transform not available")



def onClickStickyNote():
    """Handle sticky note click pickup"""
    global notePickedUp, noteObject
    if not noteObject or notePickedUp:
        return

    # Give code and hide the sticky note transform
    addToInventory(f"Safe Code: {noteCode}", "code")
    # Teleport the sticky note far outside the map and disable rendering as a fallback
    try:
        if noteObject:
            try:
                noteObject.setPosition([9999,9999,9999])
            except Exception:
                pass
            try:
                noteObject.disable(viz.RENDERING)
            except Exception:
                pass
    except Exception:
        pass

    noteObject = None
    notePickedUp = True
    print("Sticky note picked up! Code:", noteCode)

def onClickSafe():
    """Handle safe click to open code entry GUI"""
    safeGUI()

#--------------------- INETERACT -----------------------------------------------
def pickInteract():
    # Raycast straight ahead from the camera (aligned with crosshair)
    start = viz.MainView.getPosition()
    forward = viz.MainView.getMatrix().getForward()
    ray_length = 2.0
    end = [start[0] + forward[0] * ray_length,
           start[1] + forward[1] * ray_length,
           start[2] + forward[2] * ray_length]

    hit = viz.intersect(start, end)

    if not hit.valid:
        return

    node_name = getattr(hit, 'name', None)
    print(f"Clicked object: {node_name}")

    # Route interactions by name
    if node_name == 'stickyNote':
        onClickStickyNote()
    elif node_name in ('safeDoor', 'safeDoorBox'):
        onClickSafe()
    elif node_name == 'painting':
        onClickPainting()
        
vizact.onmousedown(viz.MOUSEBUTTON_LEFT, pickInteract)

# --------- INIT ----------

def initializeInventoryUI():
    createInventoryUI()
    initializeSafeTransforms()

vizact.ontimer(0.5, initializeInventoryUI)
