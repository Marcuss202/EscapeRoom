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

# --------- inventory system ----------
MAX_INVENTORY_SLOTS = 5
inventory = [None] * MAX_INVENTORY_SLOTS
inventoryUI = []
selectedSlot = 0

def createInventoryUI():
    global inventoryUI
    
    for i in range(MAX_INVENTORY_SLOTS):
        x_pos = 0.3 + (i * 0.1)
        
        slotBG = viz.addText('[ ]', parent=viz.SCREEN)
        slotBG.setPosition(x_pos, 0.1)
        slotBG.fontSize(40)
        slotBG.alignment(viz.ALIGN_CENTER_CENTER)
        if i == selectedSlot:
            slotBG.color(1, 1, 0)
        else:
            slotBG.color(0.7, 0.7, 0.7)
        
        slotText = viz.addText(str(i + 1), parent=viz.SCREEN)
        slotText.setPosition(x_pos, 0.05)
        slotText.color(1, 1, 1)
        slotText.fontSize(20)
        slotText.alignment(viz.ALIGN_CENTER_CENTER)
        
        inventoryUI.append({
            'background': slotBG,
            'slotNumber': slotText
        })

def updateInventoryUI():
    if len(inventoryUI) != MAX_INVENTORY_SLOTS:
        return
        
    for i in range(MAX_INVENTORY_SLOTS):
        if i == selectedSlot:
            inventoryUI[i]['background'].color(1, 1, 0)
        else:
            inventoryUI[i]['background'].color(0.7, 0.7, 0.7)
        
        # Priekšmetu attēlojums tiks pievienots vēlāk ar attēliem vai citiem vizuāliem elementiem

def addToInventory(itemName, itemType='generic'):
    for i in range(MAX_INVENTORY_SLOTS):
        if inventory[i] is None:
            inventory[i] = {
                'name': itemName,
                'type': itemType
            }
            if len(inventoryUI) > 0:
                updateInventoryUI()
            return True
    return False

def removeFromInventory(slotIndex):
    if 0 <= slotIndex < MAX_INVENTORY_SLOTS and inventory[slotIndex] is not None:
        removedItem = inventory[slotIndex]
        inventory[slotIndex] = None
        if len(inventoryUI) > 0:
            updateInventoryUI()
        return removedItem
    return None

def useItem(slotIndex):
    if 0 <= slotIndex < MAX_INVENTORY_SLOTS and inventory[slotIndex] is not None:
        item = inventory[slotIndex]
        removeFromInventory(slotIndex)
        return item
    return None

def selectInventorySlot(slotNumber):
    global selectedSlot
    if 0 <= slotNumber < MAX_INVENTORY_SLOTS:
        selectedSlot = slotNumber
        if len(inventoryUI) > 0:
            updateInventoryUI()

def onKey1(): selectInventorySlot(0)
def onKey2(): selectInventorySlot(1)
def onKey3(): selectInventorySlot(2)
def onKey4(): selectInventorySlot(3)
def onKey5(): selectInventorySlot(4)

def onKeyE():
    useItem(selectedSlot)

def onKeyQ():
    removeFromInventory(selectedSlot)

vizact.onkeydown('1', onKey1)
vizact.onkeydown('2', onKey2)
vizact.onkeydown('3', onKey3)
vizact.onkeydown('4', onKey4)
vizact.onkeydown('5', onKey5)
vizact.onkeydown('e', onKeyE)
vizact.onkeydown('q', onKeyQ)

# --------- safe interaction system ----------
safeCode = "1234"
safeOpen = False
currentInput = ""
codeDisplay = None
safeUI = []

def createCodeInputUI():
    global codeDisplay, safeUI
    
    background = viz.addText('━━━━━━━━━━━━━━━━━━━━━━━━', parent=viz.SCREEN)
    background.setPosition(0.5, 0.5)
    background.color(0.2, 0.2, 0.2)
    background.fontSize(30)
    background.alignment(viz.ALIGN_CENTER_CENTER)
    
    title = viz.addText('IEVADIET KODU:', parent=viz.SCREEN)
    title.setPosition(0.5, 0.6)
    title.color(1, 1, 1)
    title.fontSize(24)
    title.alignment(viz.ALIGN_CENTER_CENTER)
    
    codeDisplay = viz.addText('_ _ _ _', parent=viz.SCREEN)
    codeDisplay.setPosition(0.5, 0.5)
    codeDisplay.color(0, 1, 0)
    codeDisplay.fontSize(36)
    codeDisplay.alignment(viz.ALIGN_CENTER_CENTER)
    
    instructions = viz.addText('Ierakstiet ciparus 0-9, ESC lai aizvērtu', parent=viz.SCREEN)
    instructions.setPosition(0.5, 0.4)
    instructions.color(0.8, 0.8, 0.8)
    instructions.fontSize(16)
    instructions.alignment(viz.ALIGN_CENTER_CENTER)
    
    safeUI = [background, title, codeDisplay, instructions]

def updateCodeDisplay():
    if codeDisplay:
        display = ""
        for i in range(4):
            if i < len(currentInput):
                display += currentInput[i] + " "
            else:
                display += "_ "
        codeDisplay.message(display.strip())

def closeSafeUI():
    global safeUI, codeDisplay, currentInput
    for ui in safeUI:
        ui.remove()
    safeUI = []
    codeDisplay = None
    currentInput = ""
    viz.mouse.setTrap(viz.ON)

def onSafeKeyInput(key):
    global currentInput
    
    if len(safeUI) == 0:
        return
    
    if key in '0123456789' and len(currentInput) < 4:
        currentInput += key
        updateCodeDisplay()
        
        if len(currentInput) == 4:
            checkSafeCode()
    
    elif key == 'BackSpace' and len(currentInput) > 0:
        currentInput = currentInput[:-1]
        updateCodeDisplay()
    
    elif key == 'Escape':
        closeSafeUI()

def checkSafeCode():
    global safeOpen, currentInput
    
    if currentInput == safeCode:
        safeOpen = True
        addToInventory("Safes Atslēga", "key")
        
        successMsg = viz.addText('SAFES ATVĒRTS!', parent=viz.SCREEN)
        successMsg.setPosition(0.5, 0.3)
        successMsg.color(0, 1, 0)
        successMsg.fontSize(32)
        successMsg.alignment(viz.ALIGN_CENTER_CENTER)
        
        def removeSuccessMsg():
            successMsg.remove()
        vizact.ontimer(2, removeSuccessMsg)
        
        closeSafeUI()
    else:
        errorMsg = viz.addText('NEPAREIZS KODS!', parent=viz.SCREEN)
        errorMsg.setPosition(0.5, 0.3)
        errorMsg.color(1, 0, 0)
        errorMsg.fontSize(24)
        errorMsg.alignment(viz.ALIGN_CENTER_CENTER)
        
        def clearError():
            errorMsg.remove()
        vizact.ontimer(1.5, clearError)
        
        currentInput = ""
        updateCodeDisplay()

def openSafe():
    if not safeOpen:
        createCodeInputUI()
        viz.mouse.setTrap(viz.OFF)

vizact.onkeydown('0', lambda: onSafeKeyInput('0'))
vizact.onkeydown('1', lambda: onSafeKeyInput('1'))
vizact.onkeydown('2', lambda: onSafeKeyInput('2'))
vizact.onkeydown('3', lambda: onSafeKeyInput('3'))
vizact.onkeydown('4', lambda: onSafeKeyInput('4'))
vizact.onkeydown('5', lambda: onSafeKeyInput('5'))
vizact.onkeydown('6', lambda: onSafeKeyInput('6'))
vizact.onkeydown('7', lambda: onSafeKeyInput('7'))
vizact.onkeydown('8', lambda: onSafeKeyInput('8'))
vizact.onkeydown('9', lambda: onSafeKeyInput('9'))
vizact.onkeydown(viz.KEY_BACKSPACE, lambda: onSafeKeyInput('BackSpace'))
vizact.onkeydown(viz.KEY_ESCAPE, lambda: onSafeKeyInput('Escape'))

# --------- crosshair system ----------
crosshair = None

def createCrosshair():
    global crosshair
    crosshair = viz.addText('+', parent=viz.SCREEN)
    crosshair.setPosition(0.5, 0.5)
    crosshair.color(1, 1, 1)
    crosshair.fontSize(24)
    crosshair.alignment(viz.ALIGN_CENTER_CENTER)

# --------- mouse interaction system ----------
def onMouseDown():
    picked = viz.pick()
    if picked.valid:
        objectName = ""
        try:
            if hasattr(picked, 'getName'):
                objectName = picked.getName()
            elif hasattr(picked, 'name'):
                objectName = picked.name
            else:
                objectName = str(picked)
        except:
            objectName = str(picked)
        
        objectNameLower = objectName.lower()
        isSafe = False
        
        if 'vizchild(2)' in objectNameLower:
            isSafe = True
        
        try:
            pos = picked.getPosition()
            if (abs(pos[0] - (-10.0)) < 1.0 and 
                abs(pos[1] - 0.0) < 1.0 and 
                abs(pos[2] - (-10.0)) < 1.0):
                isSafe = True
        except:
            pass
            
        if any(keyword in objectNameLower for keyword in ['safe', 'safes', 'seifs', 'box', 'kastes', 'skapis']):
            isSafe = True
        
        if isSafe:
            openSafe()

vizact.onmousedown(viz.MOUSEBUTTON_LEFT, onMouseDown)

#---------- MODEL ------------------
room = viz.addChild('TestRoom.osgb')
room.setPosition(-10, 0, -10)
room.setScale([0.05, 0.05, 0.05])
room.enable(viz.LIGHTING)

movingBooks = room.getTransform('movingBooks') 

def kustinatGramatu():
    action = vizact.moveTo([339.81381, 120, 92.62527], time=2.0, interpolate=vizact.easeInOut)
    movingBook = movingBooks
    movingBook.addAction(action)

vizact.onkeydown('g', kustinatGramatu)

def initializeInventoryUI():
    createInventoryUI()
    updateInventoryUI()
    createCrosshair()

vizact.ontimer(0.5, initializeInventoryUI)