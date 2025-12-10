import viz
import vizcam
import vizshape
import vizact
import random
import vizinfo

viz.setOption('viz.fullscreen', '0')
viz.go()

gameStartTime = viz.tick()

gameStartTime = viz.tick()

room = viz.addChild('OldRoom.osgb')
if not room:
    print("ERROR: Failed to load room model")
else:
    print("Room model loaded successfully")
room.setPosition(10,0,0)
room.setScale([0.015,0.015,0.015])
room.enable(viz.LIGHTING)

bgMusic = viz.addAudio('../IntenseActionBgMusic.mp3')
bgMusic.volume(0.005)
bgMusic.loop(viz.LOOP)
bgMusic.play()

navigator = vizcam.WalkNavigate(forward='w', backward='s', left='a', right='d', moveScale=2, turnScale=0.5)
viz.mouse.setVisible(False)
viz.mouse.setTrap(viz.ON)
viz.MainView.collision(True)


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
        slotBG.fontSize(24)
        slotBG.alignment(viz.ALIGN_CENTER_CENTER)
        slotBG.color(1,1,0 if i == selectedSlot else 0.7)
        slotText = viz.addText(str(i+1), parent=viz.SCREEN)
        slotText.setPosition(x_pos,0.05)
        slotText.fontSize(16)
        slotText.alignment(viz.ALIGN_CENTER_CENTER)
        codeText = viz.addText('', parent=viz.SCREEN)
        codeText.setPosition(x_pos,0.105)
        codeText.fontSize(14)
        codeText.alignment(viz.ALIGN_CENTER_CENTER)
        codeText.color(1,1,0)
        codeText.visible = False
        inventoryUI.append({'background': slotBG,'slotNumber':slotText,'codeText':codeText})

def updateInventoryUI():
    for i in range(MAX_INVENTORY_SLOTS):
        inventoryUI[i]['background'].color(1,1,0 if i==selectedSlot else 0.7)
        if inventory[i]:
            if inventory[i]['type']=='code':
                codePart = inventory[i]['name'].split(': ')[1]
                inventoryUI[i]['codeText'].message(codePart)
            elif inventory[i]['type']=='hint':
                inventoryUI[i]['codeText'].message('Note')
            else:
                inventoryUI[i]['codeText'].message(inventory[i]['name'])
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
        itemType = inventory[slotIndex]['type']
        itemName = inventory[slotIndex]['name']
        
        if itemType == 'code':
            return None
        elif itemType == 'hint':
            showHint(itemName)
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

crosshair = viz.addText('+', parent=viz.SCREEN)
crosshair.setPosition(0.5,0.5)
crosshair.fontSize = 24
crosshair.alignment(viz.ALIGN_CENTER_CENTER)

noteCode = str(random.randint(1000, 9999))
notePickedUp = False

KEY_ITEM_NAME = "key"
keyObject = None
keyPickedUp = False
doorLocked = True


safePanel = None
safeTextboxes = []
enterCallback = None
keypadCallback = None
autoFocusTimer = None
hintPanel = None
hintText = None
hintTimer = None

def showHint(hintMessage):
    global hintText, hintTimer
    
    if hintText:
        hintText.remove()
    if hintTimer:
        hintTimer.remove()
    
    hintText = viz.addText(hintMessage, parent=viz.SCREEN)
    hintText.setPosition(0.05, 0.95)
    hintText.fontSize(28)
    hintText.alignment(viz.ALIGN_LEFT_TOP)
    hintText.color(1, 1, 0)
    
    def removeHint():
        global hintText, hintTimer
        if hintText:
            hintText.remove()
            hintText = None
        if hintTimer:
            hintTimer.remove()
            hintTimer = None
    
    hintTimer = vizact.ontimer(5.0, removeHint)

def safeGUI():
    global navigator, safePanel, safeTextboxes, enterCallback, keypadCallback, autoFocusTimer
    try:
        navigator.remove()
    except Exception:
        pass
    navigator = None
    
    viz.mouse.setVisible(viz.ON)
    viz.mouse.setTrap(viz.OFF)
    viz.mouse.setOverride(viz.ON)
    
    codeTextbox = viz.addTextbox()
    codeTextbox.setLength(0.5)
    codeTextbox.setPosition(.5, .5)
    codeTextbox.fontSize(48)
    codeTextbox.setFocus(True)
    safeTextboxes = [codeTextbox]

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
    
    def onEnter():
        checkSafeCode()
    
    enterCallback = vizact.onkeydown(viz.KEY_RETURN, onEnter)
    keypadCallback = vizact.onkeydown(viz.KEY_KP_ENTER, onEnter)    
    return safeTextboxes

def closeSafeGUI():
    global navigator, safePanel, safeTextboxes, enterCallback, keypadCallback, autoFocusTimer
    if safeTextboxes:
        for tb in safeTextboxes:
            tb.remove()
    safeTextboxes = []
    
    if enterCallback:
        enterCallback.remove()
        enterCallback = None
    if keypadCallback:
        keypadCallback.remove()
        keypadCallback = None
    if autoFocusTimer:
        autoFocusTimer.remove()
        autoFocusTimer = None
    
    navigator = vizcam.WalkNavigate(forward='w', backward='s', left='a', right='d', moveScale=2, turnScale=0.5)
    
    viz.mouse.setVisible(viz.OFF)
    viz.mouse.setTrap(viz.ON)
    viz.mouse.setOverride(viz.OFF)

def checkSafeCode():
    global safeTextboxes, noteCode
    if not safeTextboxes:
        return
    
    code = safeTextboxes[0].get()
    
    if code == noteCode:
        openSafeAnim()
        addToInventory("The key shall hides within the walls", "hint")
        closeSafeGUI()
    else:
        showHint("Wrong code. Try again.")
        closeSafeGUI()


safeDoor = None
safeDoorBox = None
noteObject = None
transformsInitialized = False
safeOpened = False

def initializeSafeTransforms():
    global safeDoor, safeDoorBox, noteObject, keyObject, transformsInitialized
    if transformsInitialized:
        return
    
    print("Initializing safe transforms...")
    
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
    
    try:
        keyObject = room.getTransform('key')
        print("  Key transform found!")
    except:
        print("  Key transform not found")
    
    viz.setOption('viz.linkable', True)
    transformsInitialized = True
    print("Safe transforms initialization complete")

def openSafeAnim():
    global safeOpened
    if safeDoor and not safeOpened:
        action = vizact.spin(0, -180, 0, speed=20, dur=4.0)
        safeDoor.addAction(action)
        safeOpened = True
    elif safeOpened:
        print("Safe is already open")
    else:
        print("WARNING: Cannot open safe - safeDoor transform not available")


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
    global notePickedUp, noteObject
    if not noteObject or notePickedUp:
        return

    addToInventory(f"Safe Code: {noteCode}", "code")
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

def onClickSafe():
    global safeOpened
    if safeOpened:
        return
    safeGUI()

def onClickKey():
    global keyPickedUp, keyObject
    if not keyObject or keyPickedUp:
        return
    
    addToInventory(KEY_ITEM_NAME, "generic")
    
    try:
        if keyObject:
            try:
                keyObject.setPosition([9999, 9999, 9999])
            except Exception:
                pass
    except Exception:
        pass
    
    keyObject = None
    keyPickedUp = True

def onClickDoor():
    global doorLocked
    if doorLocked:
        hasKey = any(item and item['name']==KEY_ITEM_NAME for item in inventory)
        if hasKey:
            doorLocked = False
            showOutro()
        else:
            showHint("The door is locked. You need a key.")

def showOutro():
    global navigator
    
    escapeTime = viz.tick() - gameStartTime
    minutes = int(escapeTime // 60)
    seconds = int(escapeTime % 60)
    
    try:
        navigator.remove()
    except Exception:
        pass
    navigator = None
    
    
    try:
        crosshair.remove()
    except Exception:
        pass
    
    blackScreen = viz.addTexQuad(parent=viz.SCREEN)
    blackScreen.setPosition(0.5, 0.5, 0)
    blackScreen.setScale(20, 20)
    blackScreen.color(0, 0, 0)
    
    escapeText = viz.addText('You have escaped!', parent=viz.SCREEN)
    escapeText.setPosition(0.5, 0.6)
    escapeText.fontSize(60)
    escapeText.alignment(viz.ALIGN_CENTER_CENTER)
    escapeText.color(1, 1, 1)
    
    timeText = viz.addText(f'Time: {minutes:02d}:{seconds:02d}', parent=viz.SCREEN)
    timeText.setPosition(0.5, 0.4)
    timeText.fontSize(40)
    timeText.alignment(viz.ALIGN_CENTER_CENTER)
    timeText.color(1, 1, 0)
    
    vizact.ontimer(5.0, viz.quit)
    vizact.ontimer2(5, 0, viz.quit)

def pickInteract():
    start = viz.MainView.getPosition()
    forward = viz.MainView.getMatrix().getForward()
    ray_length = 3.0
    end = [start[0] + forward[0] * ray_length,
           start[1] + forward[1] * ray_length,
           start[2] + forward[2] * ray_length]

    hit = viz.intersect(start, end)

    if not hit.valid:
        return

    node_name = getattr(hit, 'name', None)
    #print(f"Clicked object: {node_name}")

    if node_name == 'stickyNote':
        onClickStickyNote()
    elif node_name in ('safeDoor', 'safeDoorBox'):
        onClickSafe()
    elif node_name == 'painting':
        onClickPainting()
    elif node_name and 'key' in node_name.lower():
        onClickKey()
    elif node_name == 'door':
        onClickDoor()
        
vizact.onmousedown(viz.MOUSEBUTTON_LEFT, pickInteract)


def initializeInventoryUI():
    createInventoryUI()
    initializeSafeTransforms()

vizact.ontimer(0.5, initializeInventoryUI)
